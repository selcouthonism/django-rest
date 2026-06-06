from abc import ABC, abstractmethod
from typing import List, Optional
from .domain import Author, Book

class IAuthorRepository(ABC):
    @abstractmethod
    def get_all(self) -> List[Author]: pass

    @abstractmethod
    def get_by_id(self, author_id: str) -> Optional[Author]: pass

    @abstractmethod
    def save(self, author: Author) -> None: pass

    @abstractmethod
    def update(self, author: Author) -> None: pass

    @abstractmethod
    def delete(self, author_id: str) -> None: pass

class IBookRepository(ABC):
    @abstractmethod
    def get_all(self) -> List[Book]: pass

    @abstractmethod
    def get_by_id(self, book_id: str) -> Optional[Book]: pass

    @abstractmethod
    def save(self, book: Book) -> None: pass

    @abstractmethod
    def update(self, book: Book) -> None: pass

    @abstractmethod
    def delete(self, book_id: str) -> None: pass
