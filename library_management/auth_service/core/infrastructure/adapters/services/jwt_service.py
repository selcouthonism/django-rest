import jwt
import datetime
from django.conf import settings
from core.domain.interfaces.services.token_service import ITokenService
from core.domain.entities.login_credential import LoginCredential

class JwtTokenService(ITokenService):
    def generate_tokens(self, user: LoginCredential) -> dict:
        #TODO: Consider adding a unique identifier (like jti) to the token payload for better token management (e.g., blacklisting).
        # jti (JWT ID): Unique identifier; can be used to prevent the JWT from being replayed (allows a token to be used only once)
        
        access_payload = {
            'user_id': user.user_id,
            'username': user.username,
            'roles': user.roles,
            'iss': 'auth_service',
            'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRATION_MINUTES),
            'iat': datetime.datetime.now(datetime.timezone.utc)
        }
        refresh_payload = {
            'user_id': user.user_id,
            'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=settings.REFRESH_TOKEN_EXPIRATION_DAYS)
        }
        
        access_token = jwt.encode(access_payload, settings.SECRET_KEY, algorithm='HS256')
        refresh_token = jwt.encode(refresh_payload, settings.SECRET_KEY, algorithm='HS256')

        return {
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRATION_MINUTES * 60, # Return expiration time in seconds
            "refresh_token": refresh_token
        }

    def verify_access_token(self, token: str) -> dict:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    
    def verify_refresh_token(self, token: str) -> dict:
        try:
            # Refresh tokens should ideally be verified against the DB (e.g., checking if revoked)
            # For stateless JWTs, we just decode and check signature/expiration
            return jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise Exception("Refresh token expired")
        except jwt.InvalidTokenError:
            raise Exception("Invalid refresh token")