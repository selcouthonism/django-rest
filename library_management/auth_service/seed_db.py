import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auth_project.settings')
django.setup()

from django_app.models import RoleModel, UserModel, LoginCredentialModel, UserRoleModel
from django.contrib.auth.hashers import make_password

def seed():
    role, _ = RoleModel.objects.get_or_create(role_name="ADMIN")
    print("ADMIN role exists or was created successfully.")

    user, created = UserModel.objects.get_or_create(
        email="test.admin@example.com",
        defaults={
            'first_name': "test_admin",
            'last_name': "test_admin",
            'phone': "1234567890",
        }
    )
    print(f"Test user 'test_admin' {'created' if created else 'already exists'}.")

    UserRoleModel.objects.get_or_create(
        user=user,
        role=role,
    )
    print("Test user 'test_admin' assigned to 'ADMIN' role successfully.")

    credential, created = LoginCredentialModel.objects.get_or_create(
        username="test_admin",
        defaults={
            'user': user,
            'password_hash': make_password(password="securepassword123", salt="salt_0"),
            'salt': "salt_0",
        }
    )
    print(f"Login credential for 'test_admin' {'created' if created else 'already exists'}." )

if __name__ == '__main__':
    seed()