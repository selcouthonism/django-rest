from typing import Dict, List, Optional
from .interfaces import IBookRepository, IAuthorRepository
from .domain import Book, Author

class InMemoryAuthorRepository(IAuthorRepository):
    def __init__(self):
        self._db: Dict[str, Author] = {}

    def get_all(self) -> List[Author]:
        return list(self._db.values())

    def get_by_id(self, author_id: str) -> Optional[Author]:
        return self._db.get(author_id)

    def save(self, author: Author) -> None:
        self._db[author.id] = author

    def update(self, author: Author) -> None:
        if author.id in self._db:
            self._db[author.id] = author

    def delete(self, author_id: str) -> None:
        if author_id in self._db:
            del self._db[author_id]


class InMemoryBookRepository(IBookRepository):
    def __init__(self):
        self._db: Dict[str, Book] = {}

    def get_all(self) -> List[Book]:
        return list(self._db.values())

    def get_by_id(self, book_id: str) -> Optional[Book]:
        return self._db.get(book_id)

    def save(self, book: Book) -> None:
        self._db[book.id] = book

    def update(self, book: Book) -> None:
        if book.id in self._db:
            self._db[book.id] = book

    def delete(self, book_id: str) -> None:
        if book_id in self._db:
            del self._db[book_id]