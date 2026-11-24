
from abc import ABC, abstractmethod
from typing import Optional
from ...entities.refresh_token import RefreshToken

class IRefreshTokenRepository(ABC):
    @abstractmethod
    def get_by_token(self, token: str) -> Optional[RefreshToken]:
        pass

    @abstractmethod
    def get_by_token_for_update(self, token: str) -> Optional[RefreshToken]:
        pass

    @abstractmethod
    def save(self, refresh_token: RefreshToken) -> None:
        """Update or create a refresh token in the database"""
        pass

    @abstractmethod
    def revoke_all_for_user(self, user_id: int) -> None:
        """Used for security breaches (Reuse detection)"""
        pass