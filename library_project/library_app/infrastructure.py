from typing import Dict, List, Optional
from .interfaces import IBookRepository
from .domain import Book

class InMemoryBookRepository (IBookRepository):
    def __init__(self):
        # The in-memory database store
        self._db: Dict[int, Book] = {}
    
    def get_all(self) -> List[Book]:
        return list(self._db.values())

    def get_by_id(self, id: int) -> Optional[Book]:
        return self._db.get(id)

    def save(self, book: Book) -> Book:
        self._db[book.id] = book
        return book

    def update(self, book: Book) -> Optional[Book]:
        if book.id in self._db:
            self._db[book.id] = book
            return book
        return None

    def delete(self, id: int) -> None:
        if id in self._db:
            del self._db[id]