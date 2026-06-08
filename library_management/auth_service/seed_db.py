import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auth_project.settings')
django.setup()

from django_app.models import RoleModel, LoginCredentialModel, UserRoleModel
from django.contrib.auth.hashers import make_password

def seed():
    # 1. Create Roles
    admin_role, _ = RoleModel.objects.get_or_create(name="Admin")
    user_role, _ = RoleModel.objects.get_or_create(name="User")

    # 2. Create User
    if not LoginCredentialModel.objects.filter(username="test_admin").exists():
        user = LoginCredentialModel.objects.create(
            username="test_admin",
            password=make_password("securepassword123"),
            salt="", # Handled internally by Django's make_password
            is_active=True
        )
        
        # 3. Assign Role
        UserRoleModel.objects.create(user=user, role=admin_role)
        print("Test user 'test_admin' created successfully.")
    else:
        print("Test user already exists.")

if __name__ == '__main__':
    seed()