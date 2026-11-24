import datetime
from typing import Optional
from django.conf import settings
from dataclasses import dataclass

@dataclass
class RefreshToken:
    id: int
    user_id: int
    token: str
    expires_at: datetime.datetime
    revoked_at: Optional[datetime.datetime] = None
    replaced_by_token: Optional[int] = None

    @property
    def is_expired(self) -> bool:
        return datetime.datetime.now(datetime.timezone.utc) >= self.expires_at
    
    @property
    def is_revoked(self) -> bool:
        return self.revoked_at is not None
    
    @classmethod
    def create(cls, user_id: int, token: str):
        instance = cls(
            id=None,
            user_id=user_id,
            token=token,
            expires_at=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=settings.REFRESH_TOKEN_EXPIRATION_DAYS),
            revoked_at=None,
            replaced_by_token=None
        )
        return instance


