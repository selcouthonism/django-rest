from django.contrib.auth.hashers import check_password, make_password
from core.domain.interfaces.services.hash_service import IPasswordHasher

class StandardPasswordHasher(IPasswordHasher):
    def verify_password(self, plain_password: str, hashed_password: str, salt: str) -> bool:
        reconstructed_hash = make_password(plain_password, salt)
        return reconstructed_hash == hashed_password
    
        # Django's check_password handles salt extraction from the hash internally.
        # The salt parameter is accepted for interface compatibility but not needed for Django hashes.
        # return check_password(plain_password, hashed_password)
    

    # Note: If you need to create users, you would add a method here:
    def hash_password(self, plain_password: str, salt: str) -> str:
        return make_password(plain_password, salt)