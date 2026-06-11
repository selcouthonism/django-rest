from dataclasses import dataclass

@dataclass
class UserRole:
    user_id: int
    role_id: int
    is_active: bool