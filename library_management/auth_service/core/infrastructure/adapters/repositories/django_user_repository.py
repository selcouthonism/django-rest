from core.domain.entities.login_credential import LoginCredential
from core.domain.interfaces.repositories.user_repository import IUserRepository
from django_app.models import LoginCredentialModel, UserRoleModel

class DjangoUserRepository(IUserRepository):
    def get_by_username(self, username: str) -> LoginCredential:
        try:
            return self._get_login_credential(
                    username=username, 
                    is_active=True
            )
        except LoginCredentialModel.DoesNotExist:
            return None
        
    def get_by_id(self, user_id: int) -> LoginCredential:
        try:
            return self._get_login_credential(
                user_id=user_id, 
                is_active=True
            )
        except LoginCredentialModel.DoesNotExist:
            return None


    def _get_login_credential(self, **filters) -> LoginCredential:
        db_user = (
            LoginCredentialModel.objects
            .filter(**filters)
            .only(
                "user_id",
                "username",
                "password_hash",
                "salt",
                "is_active"
            )
            .get()
        )

        roles = list(
            UserRoleModel.objects
            .filter(user_id=db_user.user_id, is_active=True)
            .select_related("role")
            .values_list("role__role_name", flat=True)
        )

        return LoginCredential(
            user_id=db_user.user_id,
            username=db_user.username,
            password_hash=db_user.password_hash,
            salt=db_user.salt,
            is_active=db_user.is_active,
            roles=roles
        )
    





    
    """
    def get_by_username(self, username: str) -> LoginCredential:
        try:
            result = self._get_login_credential(username=username, is_active=True)
            return self._to_entity(result) if result else None
        
        except LoginCredentialModel.DoesNotExist:
            return None
        
    def get_by_id(self, user_id: int) -> LoginCredential:
        try:
            result = self._get_login_credential(user_id=user_id, is_active=True)
            return self._to_entity(result) if result else None

        except LoginCredentialModel.DoesNotExist:
            return None
        
    def _get_login_credential(self, **filters):
        # Single-query aggregation approach to fetch user credentials along with their active roles.
        return (
            LoginCredentialModel.objects
            .filter(**filters)
            .values(
                "user_id",
                "username",
                "password_hash",
                "salt",
                "is_active"
            )
            .annotate(
                roles=ArrayAgg(
                    "user__user_roles__role__role_name",
                    filter=Q(user__user_roles__is_active=True),
                    distinct=True
                )
            )
            .order_by("user_id")
            .first()
        )
        

    def _to_entity(self, result: dict) -> LoginCredential:
        return LoginCredential(
            user_id=result["user_id"],
            username=result["username"],
            password_hash=result["password_hash"],
            salt=result["salt"],
            is_active=result["is_active"],
            roles=result["roles"] or []
        )
    """