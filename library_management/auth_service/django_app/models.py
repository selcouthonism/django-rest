from django.db import models
from django.conf import settings
from django.utils.timezone import now
#from django.db.models import Q, UniqueConstraint

# Create your models here.

# Django Configuration & Models (The ORM Mapping)

class RoleModel(models.Model):
    id = models.BigAutoField(primary_key=True)
    role_name = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = 'role'
        managed = settings.MANAGE_DB_TABLES #  False: "These tables are managed externally, don't touch them"

class UserModel(models.Model):
    id = models.BigAutoField(primary_key=True)
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    phone = models.CharField(max_length=15)
    email = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user'
        managed = settings.MANAGE_DB_TABLES

class UserRoleModel(models.Model):
    user = models.ForeignKey(UserModel, db_column='user_id', on_delete=models.CASCADE, related_name='user_roles')
    role = models.ForeignKey(RoleModel, db_column='role_id', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_roles'
        managed = settings.MANAGE_DB_TABLES

class LoginCredentialModel(models.Model):
    username = models.CharField(max_length=64, primary_key=True)
    user = models.ForeignKey(UserModel, unique=True, db_column='user_id', on_delete=models.CASCADE, related_name='login_credentials')
    password_hash = models.CharField(max_length=255)
    salt = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'login_credential'
        managed = settings.MANAGE_DB_TABLES

class RefreshTokenModel(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(UserModel, db_column='user_id', on_delete=models.CASCADE, related_name='refresh_token')
    token = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    revoked_at = models.DateTimeField(null=True, blank=True)
    # Tracks the rotation chain. If a token is reused, we know which one replaced it.
    replaced_by_token = models.ForeignKey('self',db_column='replaced_by_token_id',on_delete=models.SET_NULL,null=True,blank=True,related_name='replaced_tokens')
    #replaced_by_token = models.CharField(max_length=255, null=True, blank=True)
    
    def is_expired(self):
        return now() >= self.expires_at
    
    class Meta:
        db_table = 'refresh_token'
        managed = settings.MANAGE_DB_TABLES
