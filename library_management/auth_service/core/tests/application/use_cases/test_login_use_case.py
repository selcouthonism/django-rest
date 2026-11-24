from django.conf import settings
if not settings.configured:
    settings.configure(
        REFRESH_TOKEN_EXPIRATION_DAYS=7,   # a default value you can later override
    )
import django
django.setup()

import datetime
import unittest
from unittest.mock import MagicMock, patch
from core.application.use_cases.login_use_case import LoginUseCase
from core.application.exceptions import AuthenticationError
from core.domain.entities.login_credential import LoginCredential
from core.domain.entities.refresh_token import RefreshToken

class TestLoginUseCase(unittest.TestCase):
    """Test Setup and Dependencies"""
    """Testing the Login Use Case"""
    def setUp(self):
        # 1. Mock our strict interface contracts
        self.mock_user_repo = MagicMock()
        self.mock_refresh_token_repo = MagicMock()
        self.mock_hasher = MagicMock()
        self.mock_token_service = MagicMock()

        # 2. Inject the mocks into our Use Case
        self.use_case = LoginUseCase(
            user_repo=self.mock_user_repo,
            refresh_token_repo=self.mock_refresh_token_repo,
            hasher=self.mock_hasher,
            token_service=self.mock_token_service
        )

        # 3. Define a standard valid user entity for testing
        self.valid_user = LoginCredential(
            user_id=1,
            username="test_admin",
            password_hash="hashed_pw123",
            roles=["Admin"]
        )

        self.refresh_token = RefreshToken(
            id=1001,
            user_id=1,
            token="valid_refresh_token",
            expires_at=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=30),
            revoked_at=None,
            replaced_by_token=None
        )

    # --- TEST CASES GO HERE ---
    @patch( "core.domain.entities.refresh_token.RefreshToken.create" )
    def test_login_success(self, mock_create):
        # Arrange
        self.mock_user_repo.get_by_username.return_value = self.valid_user
        self.mock_hasher.verify_password.return_value = True
        self.mock_token_service.generate_access_token.return_value = {
            "access_token": "valid.jwt.token",
            "token_type": "Bearer",
            "expires_in": 900
        }
        self.mock_token_service.generate_opaque_refresh_token.return_value = self.refresh_token.token
        mock_create.return_value = self.refresh_token

        # Act
        result = self.use_case.execute("test_admin", "correct_password")

        # Assert
        self.assertEqual(result["access_token"], "valid.jwt.token")
        self.mock_user_repo.get_by_username.assert_called_once_with("test_admin")
        self.mock_hasher.verify_password.assert_called_once_with(
            "correct_password", "hashed_pw123"
        )
        self.mock_token_service.generate_access_token.assert_called_once_with(self.valid_user)
        self.mock_token_service.generate_opaque_refresh_token.assert_called_once()
        mock_create.assert_called_once_with(self.valid_user.user_id, self.refresh_token.token)
        self.mock_refresh_token_repo.save.assert_called_once_with(self.refresh_token)

    def test_login_fails_when_user_not_found(self):
        # Arrange
        self.mock_user_repo.get_by_username.return_value = None

        # Act & Assert
        with self.assertRaisesRegex(AuthenticationError, "Invalid credentials"):
            self.use_case.execute("unknown_user", "any_password")
            
        # Ensure we don't bother hashing if the user isn't found (saves CPU cycles)
        #self.mock_hasher.verify_password.assert_not_called()
        
        # verify_passwor called to prevent timing attacks by always performing the hash check, even if user is not found
        self.mock_hasher.verify_password.assert_called_once_with("any_password", "")

    def test_login_fails_on_incorrect_password(self):
        # Arrange
        self.mock_user_repo.get_by_username.return_value = self.valid_user
        self.mock_hasher.verify_password.return_value = False # Simulate bad password

        # Act & Assert
        with self.assertRaisesRegex(AuthenticationError, "Invalid credentials"):
            self.use_case.execute("test_admin", "wrong_password")
        
        # Ensure token generation is never called if password fails
        self.mock_token_service.generate_access_token.assert_not_called()