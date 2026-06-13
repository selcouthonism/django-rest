import unittest
from unittest.mock import MagicMock
from core.application.use_cases.refresh_token_use_case import RefreshTokenUseCase
from core.application.exceptions import AuthenticationError
from core.domain.entities.login_credential import LoginCredential

class TestRefreshTokenUseCase(unittest.TestCase):
    """It orchestrates multiple dependencies (decoding tokens, checking database state, 
    generating new tokens) while remaining entirely decoupled from the actual frameworks doing the heavy lifting."""
    def setUp(self):
        # 1. Mock the specific interface contracts needed for this use case
        self.mock_user_repo = MagicMock()
        self.mock_token_service = MagicMock()

        # 2. Inject the mocks into the Use Case
        self.use_case = RefreshTokenUseCase(
            user_repo=self.mock_user_repo,
            token_service=self.mock_token_service
        )

        # 3. Standard valid user for predictable testing
        self.valid_user = LoginCredential(
            user_id=1,
            username="test_admin",
            password_hash="hashed_pw123",
            is_active=True,
            roles=["Admin"]
        )

        # 4. Standard new token response payload
        self.new_token_payload = {
            "access_token": "new.access.token",
            "token_type": "Bearer",
            "expires_in": 900,
            "refresh_token": "new.refresh.token"
        }

    def test_refresh_token_success(self):
        # Arrange
        valid_refresh_token = "valid.refresh.token"
        self.mock_token_service.verify_refresh_token.return_value = {"user_id": 1}
        self.mock_user_repo.get_by_id.return_value = self.valid_user
        self.mock_token_service.generate_tokens.return_value = self.new_token_payload

        # Act
        result = self.use_case.execute(valid_refresh_token)

        # Assert
        self.assertEqual(result, self.new_token_payload)
        
        # Verify the exact sequence of orchestrations
        self.mock_token_service.verify_refresh_token.assert_called_once_with(valid_refresh_token)
        self.mock_user_repo.get_by_id.assert_called_once_with(1)
        self.mock_token_service.generate_tokens.assert_called_once_with(self.valid_user)

    # ----- Business Rule Failures -----
    # Ensure the application fails gracefully and securely without needing to trigger actual HTTP 401s or 500s.
    
    def test_refresh_fails_when_token_is_missing(self):
        # Act & Assert
        with self.assertRaisesRegex(AuthenticationError, "Refresh token is required"):
            self.use_case.execute(None)
            
        with self.assertRaisesRegex(AuthenticationError, "Refresh token is required"):
            self.use_case.execute("")

        # Ensure no downstream dependencies were triggered
        self.mock_token_service.verify_refresh_token.assert_not_called()

    def test_refresh_fails_on_invalid_or_expired_token(self):
        # Arrange
        # Simulate PyJWT throwing an exception (e.g., ExpiredSignatureError)
        self.mock_token_service.verify_refresh_token.side_effect = Exception("Signature has expired")

        # Act & Assert
        with self.assertRaisesRegex(AuthenticationError, "Invalid refresh token: Signature has expired"):
            self.use_case.execute("expired.refresh.token")

        # Ensure we don't hit the database if the token is mathematically invalid
        self.mock_user_repo.get_by_id.assert_not_called()

    def test_refresh_fails_when_user_not_found(self):
        # Arrange
        self.mock_token_service.verify_refresh_token.return_value = {"user_id": 999}
        # Simulate user being deleted from DB after token was issued
        self.mock_user_repo.get_by_id.return_value = None 

        # Act & Assert
        with self.assertRaisesRegex(AuthenticationError, "User is inactive or deleted"):
            self.use_case.execute("valid.token.for.deleted.user")

        # Ensure new tokens are never generated
        self.mock_token_service.generate_tokens.assert_not_called()

    def test_refresh_fails_when_user_is_inactive(self):
        # Arrange
        self.mock_token_service.verify_refresh_token.return_value = {"user_id": 1}
        
        # Simulate user account being disabled by an admin
        inactive_user = self.valid_user
        inactive_user.is_active = False
        self.mock_user_repo.get_by_id.return_value = inactive_user

        # Act & Assert
        with self.assertRaisesRegex(AuthenticationError, "User is inactive or deleted"):
            self.use_case.execute("valid.token.for.inactive.user")

        # Ensure new tokens are never generated
        self.mock_token_service.generate_tokens.assert_not_called()