from dataclasses import dataclass

@dataclass
class Author:
    id: str
    name: str
    surname: str
    date_of_birth: str  # YYYY-MM-DD

@dataclass
class Book:
    id: str
    title: str
    published_year: int
    author: Author