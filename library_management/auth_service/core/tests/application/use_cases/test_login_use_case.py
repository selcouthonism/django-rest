import unittest
from unittest.mock import MagicMock
from core.application.use_cases.login_use_case import LoginUseCase
from core.application.exceptions import AuthenticationError
from core.domain.entities.login_credential import LoginCredential

class TestLoginUseCase(unittest.TestCase):
    """Test Setup and Dependencies"""
    """Testing the Login Use Case"""
    def setUp(self):
        # 1. Mock our strict interface contracts
        self.mock_user_repo = MagicMock()
        self.mock_hasher = MagicMock()
        self.mock_token_service = MagicMock()

        # 2. Inject the mocks into our Use Case
        self.use_case = LoginUseCase(
            user_repo=self.mock_user_repo,
            hasher=self.mock_hasher,
            token_service=self.mock_token_service
        )

        # 3. Define a standard valid user entity for testing
        self.valid_user = LoginCredential(
            user_id=1,
            username="test_admin",
            password_hash="hashed_pw123",
            is_active=True,
            roles=["Admin"]
        )

    # --- TEST CASES GO HERE ---
    def test_login_success(self):
        # Arrange
        self.mock_user_repo.get_by_username.return_value = self.valid_user
        self.mock_hasher.verify_password.return_value = True
        self.mock_token_service.generate_tokens.return_value = {
            "access_token": "valid.jwt.token",
            "token_type": "Bearer",
            "expires_in": 900,
            "refresh_token": "valid.refresh.token"
        }

        # Act
        result = self.use_case.execute("test_admin", "correct_password")

        # Assert
        self.assertEqual(result["access_token"], "valid.jwt.token")
        self.mock_user_repo.get_by_username.assert_called_once_with("test_admin")
        self.mock_hasher.verify_password.assert_called_once_with(
            "correct_password", "hashed_pw123"
        )
        self.mock_token_service.generate_tokens.assert_called_once_with(self.valid_user)

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

    def test_login_fails_when_user_inactive(self):
        # Arrange
        inactive_user = self.valid_user
        inactive_user.is_active = False
        self.mock_user_repo.get_by_username.return_value = inactive_user

        # Act & Assert
        with self.assertRaisesRegex(AuthenticationError, "Invalid credentials"):
            self.use_case.execute("test_admin", "correct_password")

    def test_login_fails_on_incorrect_password(self):
        # Arrange
        self.mock_user_repo.get_by_username.return_value = self.valid_user
        self.mock_hasher.verify_password.return_value = False # Simulate bad password

        # Act & Assert
        with self.assertRaisesRegex(AuthenticationError, "Invalid credentials"):
            self.use_case.execute("test_admin", "wrong_password")
        
        # Ensure token generation is never called if password fails
        self.mock_token_service.generate_tokens.assert_not_called()