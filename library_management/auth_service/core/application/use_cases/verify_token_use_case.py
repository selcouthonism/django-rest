from core.domain.interfaces.services.token_service import ITokenService
from ..exceptions import AuthenticationError

class VerifyTokenUseCase:
    def __init__(self, token_service: ITokenService):
        self.token_service = token_service

    def execute(self, token: str) -> dict:
        try:
            return self.token_service.verify_access_token(token)
        except Exception:
            raise AuthenticationError("Invalid or expired token")