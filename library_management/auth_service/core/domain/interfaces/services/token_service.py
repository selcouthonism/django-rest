from abc import ABC, abstractmethod
from ...entities.login_credential import LoginCredential

class ITokenService(ABC):
    @abstractmethod
    def generate_access_token(self, user: LoginCredential) -> dict:
        """Generates authentication tokens for the user. Returns {access_token, token_type, expires_in}"""
        pass

    @abstractmethod
    def generate_opaque_refresh_token(self) -> str:
        """Generates a cryptographically secure random string"""
        pass
        
    @abstractmethod
    def verify_access_token(self, token: str) -> dict:
        """Returns decoded payload if valid, raises exception if not."""
        pass

    @abstractmethod
    def verify_refresh_token(self, token: str) -> dict:
        """Returns decoded payload if refresh token is valid."""
        pass