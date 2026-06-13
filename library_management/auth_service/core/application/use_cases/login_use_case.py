from core.domain.interfaces.repositories.user_repository import IUserRepository
from core.domain.interfaces.services.hash_service import IPasswordHasher
from core.domain.interfaces.services.token_service import ITokenService
from ..exceptions import AuthenticationError

class LoginUseCase:
    def __init__(self, user_repo: IUserRepository, hasher: IPasswordHasher, token_service: ITokenService):
        self.user_repo = user_repo
        self.hasher = hasher
        self.token_service = token_service

    def execute(self, username: str, password: str) -> dict:
        user = self.user_repo.get_by_username(username)
        if not user or not user.is_active:
            # To prevent timing attacks, we should still call verify_password with dummy data here to make the response time consistent regardless of whether the user exists or not.
            self.hasher.verify_password(password, "")
            raise AuthenticationError("Invalid credentials")

        if not self.hasher.verify_password(password, user.password_hash):
            raise AuthenticationError("Invalid credentials")

        return self.token_service.generate_tokens(user)