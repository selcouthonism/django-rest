from core.domain.entities.login_credential import LoginCredential
from core.domain.interfaces.repositories.user_repository import IUserRepository
from django_app.models import LoginCredentialModel

class DjangoUserRepository(IUserRepository):
    def get_by_username(self, username: str) -> LoginCredential:
        try:
            db_user = LoginCredentialModel.objects.prefetch_related('userrolemodel_set__role').get(username=username)
            roles = [ur.role.name for ur in db_user.userrolemodel_set.filter(is_active=True)]
            
            return LoginCredential(
                user_id=db_user.user_id,
                username=db_user.username,
                password_hash=db_user.password,
                salt=db_user.salt,
                is_active=db_user.is_active,
                roles=roles
            )
        except LoginCredentialModel.DoesNotExist:
            return None