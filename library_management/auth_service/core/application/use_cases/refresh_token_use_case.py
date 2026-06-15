from core.domain.interfaces.repositories.user_repository import IUserRepository
from core.domain.interfaces.services.token_service import ITokenService
from ..exceptions import AuthenticationError

class RefreshTokenUseCase:
    """RefreshTokenUseCase takes the refresh token, verifies it, fetches the latest user data 
        (to ensure they haven't been deactivated or had roles changed since the last login), 
        and generates a new token pair."""
    
    def __init__(self, user_repo: IUserRepository, token_service: ITokenService):
        self.user_repo = user_repo
        self.token_service = token_service

    def execute(self, refresh_token: str) -> dict:
        if not refresh_token:
            raise AuthenticationError("Refresh token is required")

        try:
            # 1. Verify the refresh token is mathematically valid and not expired
            payload = self.token_service.verify_refresh_token(refresh_token)
            user_id = payload.get('user_id')
            
            # 2. Re-fetch the user to ensure they are still active and get current roles
            user = self.user_repo.get_by_id(user_id) 
            
            if not user:
                # Security Concern: Gives infomration about system. To mitigate this, we could log the event and return a generic error message.
                raise AuthenticationError("User is deleted")

            # 3. Generate a fresh pair of tokens
            return self.token_service.generate_tokens(user)

        except Exception as e:
            raise AuthenticationError(f"Invalid refresh token: {str(e)}")