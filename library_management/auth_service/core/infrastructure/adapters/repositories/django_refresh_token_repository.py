from core.domain.interfaces.repositories.refresh_token_repository import IRefreshTokenRepository
from core.domain.entities.refresh_token import RefreshToken
from django_app.models import RefreshTokenModel

import datetime

class DjangoRefreshTokenRepository(IRefreshTokenRepository):
    def get_by_token(self, token: str) -> RefreshToken:
        try:
            db_token = RefreshTokenModel.objects.get(token=token)
            return RefreshToken(
                id=db_token.id,
                token=db_token.token,
                user_id=db_token.user_id,
                expires_at=db_token.expires_at,
                revoked_at=db_token.revoked_at,
                replaced_by_token=db_token.replaced_by_token
            )
        except RefreshTokenModel.DoesNotExist:
            return None

    def get_by_token_for_update(self, token: str) -> RefreshToken:
        try:
            db_token = RefreshTokenModel.objects.select_for_update().get(token=token)
            return RefreshToken(
                id=db_token.id,
                token=db_token.token,
                user_id=db_token.user_id,
                expires_at=db_token.expires_at,
                revoked_at=db_token.revoked_at,
                replaced_by_token=db_token.replaced_by_token
            )
        except RefreshTokenModel.DoesNotExist:
            return None

    def save(self, rt_entity: RefreshToken) -> None:
        db_token, _ = RefreshTokenModel.objects.update_or_create(
            token=rt_entity.token,
            defaults={
                'user_id': rt_entity.user_id,
                'expires_at': rt_entity.expires_at,
                'revoked_at': rt_entity.revoked_at,
                'replaced_by_token': rt_entity.replaced_by_token
            }
        )
        rt_entity.id = db_token.id

    def revoke_all_for_user(self, user_id: int) -> None:
        RefreshTokenModel.objects.filter(user_id=user_id, revoked_at=None).update(revoked_at=datetime.datetime.now(datetime.timezone.utc))