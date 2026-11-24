from core.domain.interfaces.repositories.user_repository import IUserRepository
from core.domain.interfaces.repositories.refresh_token_repository import IRefreshTokenRepository
from core.domain.interfaces.services.hash_service import IPasswordHasher
from core.domain.interfaces.services.token_service import ITokenService
from core.domain.entities.refresh_token import RefreshToken
from ..exceptions import AuthenticationError

class LoginUseCase:
    def __init__(self, user_repo: IUserRepository, refresh_token_repo: IRefreshTokenRepository,
                 hasher: IPasswordHasher, token_service: ITokenService):
        self.user_repo = user_repo
        self.refresh_token_repo = refresh_token_repo
        self.hasher = hasher
        self.token_service = token_service

    def execute(self, username: str, password: str) -> dict:
        user = self.user_repo.get_by_username(username)
        if not user:
            # To prevent timing attacks, we should still call verify_password with dummy data here to make the response time consistent regardless of whether the user exists or not.
            self.hasher.verify_password(password, "")
            raise AuthenticationError("Invalid credentials")

        if not self.hasher.verify_password(password, user.password_hash):
            raise AuthenticationError("Invalid credentials")
        
        # Generate access token and refresh token and save the refresh token to the database
        access_data = self.token_service.generate_access_token(user)
        refresh_token_str = self.token_service.generate_opaque_refresh_token()
        new_rt_entity = RefreshToken.create(user.user_id, refresh_token_str)
        self.refresh_token_repo.save(new_rt_entity)

        access_data["refresh_token"] = refresh_token_str
        return access_data