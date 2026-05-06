from dataclasses import dataclass

@dataclass
class Book:
    id: int
    title: str
    author_id: int
    published_year: int