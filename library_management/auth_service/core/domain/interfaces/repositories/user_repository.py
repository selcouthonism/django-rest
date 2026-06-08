from abc import ABC, abstractmethod
from typing import Optional
from ...entities.login_credential import LoginCredential

class IUserRepository(ABC):
    @abstractmethod
    def get_by_username(self, username: str) -> Optional[LoginCredential]:
        pass