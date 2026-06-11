from dataclasses import dataclass

@dataclass
class Role:
    id: int
    name: str  # "Admin" | "User" | "Support"