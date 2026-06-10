import unittest
from unittest.mock import MagicMock
from core.application.use_cases.verify_token_use_case import VerifyTokenUseCase
from core.application.exceptions import AuthenticationError

class TestVerifyTokenUseCase(unittest.TestCase):
    """Testing the Verify Token Use Case"""
    def setUp(self):
        self.mock_token_service = MagicMock()
        self.use_case = VerifyTokenUseCase(token_service=self.mock_token_service)

    def test_verify_success_returns_payload(self):
        # Arrange
        expected_payload = {
            "user_id": 1,
            "username": "test_admin",
            "roles": ["Admin"]
        }
        self.mock_token_service.verify_access_token.return_value = expected_payload

        # Act
        result = self.use_case.execute("some.valid.token")

        # Assert
        self.assertEqual(result, expected_payload)
        self.mock_token_service.verify_access_token.assert_called_once_with("some.valid.token")

    def test_verify_fails_on_invalid_or_expired_token(self):
        # Arrange
        # Simulate the JWT library throwing an exception (e.g., ExpiredSignatureError)
        self.mock_token_service.verify_access_token.side_effect = Exception("Token expired")

        # Act & Assert
        with self.assertRaisesRegex(AuthenticationError, "Invalid or expired token"):
            self.use_case.execute("some.expired.token")