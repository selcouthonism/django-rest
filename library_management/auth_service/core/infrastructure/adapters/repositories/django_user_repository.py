from core.domain.entities.login_credential import LoginCredential
from core.domain.interfaces.repositories.user_repository import IUserRepository
from django_app.models import LoginCredentialModel

class DjangoUserRepository(IUserRepository):
    def get_by_username(self, username: str) -> LoginCredential:
        try:
            db_user = (
                   LoginCredentialModel.objects
                   .select_related('user')
                   .prefetch_related('user__user_roles__role')
                   .get(username=username)
            )
                   
            #roles = [ur.role.role_name for ur in db_user.user.user_roles.filter(is_active=True)]
            roles = [ur.role.role_name for ur in db_user.user.user_roles.all() if ur.is_active]

            return LoginCredential(
                user_id=db_user.user_id,
                username=db_user.username,
                password_hash=db_user.password_hash,
                salt=db_user.salt,
                is_active=db_user.is_active,
                roles=roles
            )
        except LoginCredentialModel.DoesNotExist:
            return None