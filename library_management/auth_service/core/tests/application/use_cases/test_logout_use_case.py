import datetime
import os
import unittest
from unittest.mock import MagicMock

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "auth_project.settings")

import django

django.setup()

from core.application.use_cases.logout_use_case import LogoutUseCase
from core.domain.entities.refresh_token import RefreshToken


class TestLogoutUseCase(unittest.TestCase):
    def setUp(self):
        self.refresh_repo = MagicMock()
        self.use_case = LogoutUseCase(refresh_repo=self.refresh_repo)
        self.refresh_token = RefreshToken(
            id=10,
            user_id=1,
            token="valid.refresh.token",
            expires_at=datetime.datetime.now(datetime.timezone.utc)
            + datetime.timedelta(days=7),
        )

    def test_logout_revokes_active_refresh_token(self):
        self.refresh_repo.get_by_token_for_update.return_value = self.refresh_token

        result = self.use_case.execute(self.refresh_token.token)

        self.assertIsNone(result)
        self.refresh_repo.get_by_token_for_update.assert_called_once_with(
            self.refresh_token.token
        )
        self.refresh_repo.save.assert_called_once_with(self.refresh_token)
        self.assertIsNotNone(self.refresh_token.revoked_at)
        self.assertIsNotNone(self.refresh_token.revoked_at.tzinfo)

    def test_logout_does_not_save_when_token_does_not_exist(self):
        self.refresh_repo.get_by_token_for_update.return_value = None

        result = self.use_case.execute("unknown.refresh.token")

        self.assertIsNone(result)
        self.refresh_repo.get_by_token_for_update.assert_called_once_with(
            "unknown.refresh.token"
        )
        self.refresh_repo.save.assert_not_called()

    def test_logout_does_not_save_already_revoked_token(self):
        self.refresh_token.revoked_at = datetime.datetime.now(datetime.timezone.utc)
        self.refresh_repo.get_by_token_for_update.return_value = self.refresh_token

        result = self.use_case.execute(self.refresh_token.token)

        self.assertIsNone(result)
        self.refresh_repo.get_by_token_for_update.assert_called_once_with(
            self.refresh_token.token
        )
        self.refresh_repo.save.assert_not_called()
