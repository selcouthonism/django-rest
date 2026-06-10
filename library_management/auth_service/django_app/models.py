from django.db import models

# Create your models here.

# Django Configuration & Models (The ORM Mapping)

class RoleModel(models.Model):
    id = models.BigAutoField(primary_key=True)
    role_name = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = 'role'

class UserModel(models.Model):
    id = models.BigAutoField(primary_key=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15, unique=True)
    email = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True, db_column='created_at')

    class Meta:
        db_table = 'user'

class UserRoleModel(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(UserModel, db_column='user_id', on_delete=models.RESTRICT, related_name='user_roles')
    role = models.ForeignKey(RoleModel, db_column='role_id', on_delete=models.RESTRICT)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, db_column='created_at')

    class Meta:
        db_table = 'user_roles'
        unique_together = ('user', 'role')

class LoginCredentialModel(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(UserModel, db_column='user_id', on_delete=models.CASCADE, related_name='login_credentials')
    username = models.CharField(max_length=255, unique=True)
    password_hash = models.CharField(max_length=255)
    salt = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, db_column='created_at')

    class Meta:
        db_table = 'login_credential'
