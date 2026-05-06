from abc import ABC, abstractmethod
from typing import List, Optional
from .domain import Book


class IBookRepository(ABC): 
    @abstractmethod
    def get_all(self) -> List[Book]:
        pass
    
    @abstractmethod
    def get_by_id(self, id: int) -> Optional[Book]:
        pass

    @abstractmethod
    def save(self, book: Book) -> Book:
        pass

    @abstractmethod
    def update(self, book: Book) -> Optional[Book]:
        pass

    @abstractmethod
    def delete(self, id: int) -> None:
        pass