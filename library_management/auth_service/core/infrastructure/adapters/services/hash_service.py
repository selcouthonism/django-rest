from django.contrib.auth.hashers import check_password, make_password
from core.domain.interfaces.services.hash_service import IPasswordHasher

class StandardPasswordHasher(IPasswordHasher):
    def verify_password(self, plain_password: str, hashed_password: str, salt: str) -> bool:
        # Django's check_password handles the salt internally if it was created via make_password,
        # but if you have a custom salt requirement from a legacy system, you can concatenate it here.
        # For standard Django hashes:
        return check_password(plain_password, hashed_password)

    # Note: If you need to create users, you would add a method here:
    def hash_password(self, plain_password: str, salt: str) -> str:
        return make_password(plain_password)