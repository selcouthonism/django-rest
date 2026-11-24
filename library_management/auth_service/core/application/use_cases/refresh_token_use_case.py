import datetime
import logging
from django.db import transaction

from core.domain.interfaces.repositories.user_repository import IUserRepository
from core.domain.interfaces.repositories.refresh_token_repository import IRefreshTokenRepository
from core.domain.interfaces.services.token_service import ITokenService
from core.domain.entities.refresh_token import RefreshToken
from ..exceptions import AuthenticationError

logger = logging.getLogger(__name__)

class RefreshTokenUseCase:
    """RefreshTokenUseCase takes the refresh token, verifies it, fetches the latest user data 
        (to ensure they haven't been deactivated or had roles changed since the last login), 
        and generates a new token pair."""
    
    def __init__(self, user_repo: IUserRepository, refresh_token_repo: IRefreshTokenRepository, token_service: ITokenService):
        self.user_repo = user_repo
        self.refresh_token_repo = refresh_token_repo
        self.token_service = token_service

    def execute(self, refresh_token: str) -> dict:
        if not refresh_token:
            raise AuthenticationError("Refresh token is required")

        reuse_detected = False

        with transaction.atomic():
            # Read refresh_token entity and validate it
            rt_entity = self.refresh_token_repo.get_by_token_for_update(refresh_token)
            if not rt_entity:
                raise AuthenticationError("Invalid refresh token")

            # AUTH0 REUSE DETECTION: 
            # If a token is already revoked but someone tries to use it anyway, 
            # it implies the token was stolen. Revoke ALL tokens for this user.
            if rt_entity.is_revoked:
                self.refresh_token_repo.revoke_all_for_user(rt_entity.user_id)
                # TODO: Log this as a critical security event in a real app!
                logger.error("Token reuse detected. Account protected.")
                reuse_detected = True
            
            else:
                if rt_entity.is_expired:
                    logger.error("Refresh token expired. Please log in again.")
                    raise AuthenticationError("Invalid refresh token")
            
                # Read user
                user = self.user_repo.get_by_id(rt_entity.user_id)
                if not user:
                    # TODO: Security Concern: Gives infomration about system. To mitigate this, we could log the event and return a generic error message.
                    logger.error("Invalid credentials. (User + {0} + not found)".format(rt_entity.user_id))
                    raise AuthenticationError("Invalid refresh token")
                
                # AUTH0 ROTATION: Issue new token pair, Invalidate old token, and link the old token to the new one for audit purposes.
                # Create new token row
                new_token = self.token_service.generate_opaque_refresh_token()
                new_rt_entity = RefreshToken.create(user.user_id, new_token)
                self.refresh_token_repo.save(new_rt_entity)

                # Update old token row (revoke it)
                rt_entity.revoked_at = datetime.datetime.now(datetime.timezone.utc)
                rt_entity.replaced_by_token = new_rt_entity.id
                self.refresh_token_repo.save(rt_entity)

                # Test the following code to see if it works as expected. If it does, we can remove the above two save calls and use the following method instead.
                '''
                new_token = self.token_service.generate_opaque_refresh_token()
                new_entity = RefreshToken.create(user.user_id, new_token)
                new_entity = self.refresh_token_repo.create(new_entity)  # Return saved entity with ID

                self.refresh_token_repo.revoke_and_link(
                    old_token_id=rt_entity.id,
                    new_token_id=new_entity.id,
                )
                '''

                # Generate new access token
                access_data = self.token_service.generate_access_token(user)
                access_data["refresh_token"] = new_token

        # Must be outside atomic so reuse-triggered revocations commit.
        if reuse_detected:
            raise AuthenticationError("Invalid refresh token")
        
        return access_data
    

    
    def _validate_refresh_token(self, rt_entity: RefreshToken) -> None:
        """Validate the provided refresh token."""
        if not rt_entity:
            raise AuthenticationError("Invalid refresh token")
        
        # AUTH0 REUSE DETECTION: 
        # If a token is already revoked but someone tries to use it anyway, 
        # it implies the token was stolen. Revoke ALL tokens for this user.
        if rt_entity.is_revoked:
            self.refresh_token_repo.revoke_all_for_user(rt_entity.user_id)
            # TODO: Log this as a critical security event in a real app!
            raise AuthenticationError("Token reuse detected. Account protected.")

        if rt_entity.is_expired:
            raise AuthenticationError("Refresh token expired. Please log in again.")