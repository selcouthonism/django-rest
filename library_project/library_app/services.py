from typing import List, Optional
from .domain import Book
from .interfaces import IBookRepository
import random


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

    def create_book(self, book_data: dict) -> Book:
        if not isinstance(book_data, dict):
            raise ValueError("Invalid book payload")

        # validate required fields
        required_keys = {"title", "author_id", "published_year"}
        missing_keys = required_keys - book_data.keys()
        if missing_keys:
            raise ValueError(f"Missing required fields: {missing_keys}")

        book = Book(
            id=random.randint(100000, 999999),
            title=str(book_data["title"]),
            author_id=int(book_data["author_id"]),
            published_year=int(book_data["published_year"]),
        )
        self.repository.save(book)
        return book

    def update_book(self, id: int, book_data: dict) -> Book:
        existing_book = self.get_book_by_id(id)
        updated_book = Book(
            id=id,
            title=str(book_data.get("title") or existing_book.title),
            author_id=int(book_data.get("author_id") or existing_book.author_id),
            published_year=int(book_data.get("published_year") or existing_book.published_year),
            
            #If a key exists with value None (e.g., {"author_id": None}), int(None) raises TypeError.
            #title=str(book_data.get("title", existing_book.title)),
            #author_id=int(book_data.get("author_id", existing_book.author_id)),
            #published_year=int(book_data.get("published_year", existing_book.published_year)),
        )
        self.repository.update(updated_book)
        return updated_book

    def delete_book(self, id: int) -> None:
        self.get_book_by_id(id)
        self.repository.delete(id)
