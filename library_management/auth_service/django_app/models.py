from django.db import models

# Create your models here.

# Django Configuration & Models (The ORM Mapping)

class RoleModel(models.Model):
    name = models.CharField(max_length=50) # "Admin", "User", "Support"

class LoginCredentialModel(models.Model):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    salt = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

class UserRoleModel(models.Model):
    user = models.ForeignKey(LoginCredentialModel, on_delete=models.CASCADE)
    role = models.ForeignKey(RoleModel, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
