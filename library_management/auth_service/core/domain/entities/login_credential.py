from dataclasses import dataclass
from typing import List

@dataclass
class LoginCredential:
    user_id: int
    username: str
    password_hash: str
    is_active: bool
    roles: List[str] = None