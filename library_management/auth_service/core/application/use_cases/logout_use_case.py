
import datetime
from core.domain.interfaces.repositories.refresh_token_repository import IRefreshTokenRepository

class LogoutUseCase:
    def __init__(self, refresh_repo: IRefreshTokenRepository):
        self.refresh_repo = refresh_repo
        
    def execute(self, token_str: str) -> None:
        rt_entity = self.refresh_repo.get_by_token_for_update(token_str)
        
        if rt_entity and not rt_entity.is_revoked:
            rt_entity.revoked_at = datetime.datetime.now(datetime.timezone.utc)
            self.refresh_repo.save(rt_entity)