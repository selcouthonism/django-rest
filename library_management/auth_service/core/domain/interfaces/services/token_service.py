from abc import ABC, abstractmethod
from ...entities.login_credential import LoginCredential

class ITokenService(ABC):
    @abstractmethod
    def generate_tokens(self, user: LoginCredential) -> dict:
        """Generates authentication tokens for the user. Returns {access_token, token_type, expires_in, refresh_token}"""
        pass
        
    @abstractmethod
    def verify_access_token(self, token: str) -> dict:
        """Returns decoded payload if valid, raises exception if not."""
        pass

    @abstractmethod
    def verify_refresh_token(self, token: str) -> dict:
        """Returns decoded payload if refresh token is valid."""
        pass