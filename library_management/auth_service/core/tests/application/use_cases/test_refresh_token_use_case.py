import os
import unittest
import datetime
from unittest.mock import MagicMock, patch

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "auth_project.settings")

import django
django.setup()

from core.application.use_cases.refresh_token_use_case import RefreshTokenUseCase
from core.application.exceptions import AuthenticationError
from core.domain.entities.login_credential import LoginCredential
from core.domain.entities.refresh_token import RefreshToken

class TestRefreshTokenUseCase(unittest.TestCase):
    """It orchestrates multiple dependencies (decoding tokens, checking database state, 
    generating new tokens) while remaining entirely decoupled from the actual frameworks doing the heavy lifting."""
    def setUp(self):
        # 1. Mock the specific interface contracts needed for this use case
        self.mock_user_repo = MagicMock()
        self.mock_refresh_token_repo = MagicMock()
        self.mock_token_service = MagicMock()

        # 2. Inject the mocks into the Use Case
        self.use_case = RefreshTokenUseCase(
            user_repo=self.mock_user_repo,
            refresh_token_repo=self.mock_refresh_token_repo,
            token_service=self.mock_token_service
        )

        # 3. Standard valid user for predictable testing
        self.valid_user = LoginCredential(
            user_id=1,
            username="test_admin",
            password_hash="hashed_pw123",
            roles=["Admin"]
        )

        # 4. Standard new token response payload
        self.new_token_payload = {
            "access_token": "new.access.token",
            "token_type": "Bearer",
            "expires_in": 900,
            "refresh_token": "new.refresh.token"
        }

    def make_refresh_token(self, *, revoked=False, expired=False):
        expires_at = datetime.datetime.now(datetime.timezone.utc)
        if expired:
            expires_at -= datetime.timedelta(seconds=1)
        else:
            expires_at += datetime.timedelta(days=7)

        revoked_at = datetime.datetime.now(datetime.timezone.utc) if revoked else None
        return RefreshToken(
            id=10,
            token="valid.refresh.token",
            user_id=1,
            expires_at=expires_at,
            revoked_at=revoked_at
        )

    @patch("core.application.use_cases.refresh_token_use_case.RefreshToken.create")
    def test_refresh_token_success(self, mock_create):
        # Arrange
        valid_refresh_token = "valid.refresh.token"
        old_refresh_token = self.make_refresh_token()
        new_refresh_token = RefreshToken(
            id=11,
            token="new.refresh.token",
            user_id=1,
            expires_at=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7)
        )
        mock_create.return_value = new_refresh_token
        self.mock_user_repo.get_by_id.return_value = self.valid_user
        self.mock_refresh_token_repo.get_by_token_for_update.return_value = old_refresh_token
        self.mock_token_service.generate_opaque_refresh_token.return_value = "new.refresh.token"
        self.mock_token_service.generate_access_token.return_value = {
            "access_token": "new.access.token",
            "token_type": "Bearer",
            "expires_in": 900
        }

        # Act
        result = self.use_case.execute(valid_refresh_token)

        # Assert
        self.assertEqual(result, self.new_token_payload)
        self.mock_refresh_token_repo.get_by_token_for_update.assert_called_once_with(valid_refresh_token)
        self.mock_user_repo.get_by_id.assert_called_once_with(1)
        self.mock_token_service.generate_opaque_refresh_token.assert_called_once()
        self.mock_token_service.generate_access_token.assert_called_once_with(self.valid_user)
        self.assertEqual(self.mock_refresh_token_repo.save.call_count, 2)
        self.assertIsNotNone(old_refresh_token.revoked_at)
        self.assertIsNotNone(old_refresh_token.replaced_by_token)

    # ----- Business Rule Failures -----
    # Ensure the application fails gracefully and securely without needing to trigger actual HTTP 401s or 500s.
    
    def test_refresh_fails_when_token_is_missing(self):
        # Act & Assert
        with self.assertRaisesRegex(AuthenticationError, "Refresh token is required"):
            self.use_case.execute(None)
            
        with self.assertRaisesRegex(AuthenticationError, "Refresh token is required"):
            self.use_case.execute("")

        # Ensure no downstream dependencies were triggered
        self.mock_refresh_token_repo.get_by_token_for_update.assert_not_called()

    def test_refresh_fails_on_invalid_token(self):
        # Arrange
        self.mock_refresh_token_repo.get_by_token_for_update.return_value = None

        # Act & Assert
        with self.assertRaisesRegex(AuthenticationError, "Invalid refresh token"):
            self.use_case.execute("unknown.refresh.token")

        self.mock_user_repo.get_by_id.assert_not_called()
        self.mock_token_service.generate_opaque_refresh_token.assert_not_called()

    def test_refresh_fails_on_expired_token(self):
        # Arrange
        expired_refresh_token = self.make_refresh_token(expired=True)
        self.mock_refresh_token_repo.get_by_token_for_update.return_value = expired_refresh_token

        # Act & Assert
        with self.assertRaisesRegex(AuthenticationError, "Invalid refresh token"):
            self.use_case.execute(expired_refresh_token.token)

        self.mock_user_repo.get_by_id.assert_not_called()
        self.mock_token_service.generate_opaque_refresh_token.assert_not_called()

    def test_refresh_fails_when_user_not_found(self):
        # Arrange
        deleted_user_refresh_token = self.make_refresh_token()
        deleted_user_refresh_token.user_id = 999
        self.mock_refresh_token_repo.get_by_token_for_update.return_value = deleted_user_refresh_token
        self.mock_user_repo.get_by_id.return_value = None 

        # Act & Assert
        with self.assertRaisesRegex(AuthenticationError, "Invalid refresh token"):
            self.use_case.execute("valid.token.for.deleted.user")

        self.mock_user_repo.get_by_id.assert_called_once_with(999)
        self.mock_token_service.generate_opaque_refresh_token.assert_not_called()

    def test_revoked_token_triggers_reuse_detection(self):
        # Arrange
        revoked_refresh_token = self.make_refresh_token(revoked=True)
        self.mock_refresh_token_repo.get_by_token_for_update.return_value = revoked_refresh_token

        # Act & Assert
        with self.assertRaisesRegex(AuthenticationError, "Invalid refresh token"):
            self.use_case.execute(revoked_refresh_token.token)

        self.mock_refresh_token_repo.revoke_all_for_user.assert_called_once_with(1)
        self.mock_user_repo.get_by_id.assert_not_called()
        self.mock_token_service.generate_opaque_refresh_token.assert_not_called()