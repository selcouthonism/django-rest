from dataclasses import dataclass
from datetime import date

@dataclass
class Book:
    id: int
    title: str
    author_id: int
    published_year: str