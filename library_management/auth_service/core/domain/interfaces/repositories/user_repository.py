from abc import ABC, abstractmethod
from typing import Optional
from ...entities.login_credential import LoginCredential

class IUserRepository(ABC):
    @abstractmethod
    def get_by_username(self, username: str) -> Optional[LoginCredential]:
        """Get active LoginCredential by username, return None if not exist"""
        pass

    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[LoginCredential]:
        """Get active LoginCredential by user_id, return None if not exist"""
        pass