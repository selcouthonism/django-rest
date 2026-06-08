from abc import ABC, abstractmethod

class IPasswordHasher(ABC):
    @abstractmethod
    def verify_password(self, plain_password: str, hashed_password: str, salt: str) -> bool:
        pass