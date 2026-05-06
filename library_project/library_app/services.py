from typing import List, Optional, Dict
from .models import Book
from .interfaces import IBookRepository

class BookService:
    def __init__(self, repository: IBookRepository):
        self.repository = repository

    def get_all_books(self) -> List[Book]:
        return self.repository.get_all()

    def get_book_by_id(self, id: int) -> Book:
        existing_book = self.repository.get_by_id(id)
        if not existing_book:
            raise ValueError(f"Book with ID '{id}' does not exist.")
        return existing_book
    
    def create_book(self, book_data: Book) -> Book:
        book = Book(**book_data)
        self.repository.save(book)
        return book

    def update_book(self, id: int, book_data: Book) -> Book:
        # Check if the book exists before updating
        existing_book = self.get_book_by_id(id)
        updated_book = Book(id=id, **book_data)
        self.repository.update(updated_book)
        return updated_book

    def delete_book(self, id: int) -> None:
         # Check if the book exists before deleting
        existing_book = self.get_book_by_id(id)
        self.repository.delete(id)
