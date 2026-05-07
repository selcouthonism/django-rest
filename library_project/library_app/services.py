import uuid
from typing import List, Optional
from .domain import Book, Author
from .interfaces import IBookRepository, IAuthorRepository

class AuthorService:
    def __init__(self, repository: IAuthorRepository):
        self.repo = repository

    def get_all(self) -> List[Author]:
        return self.repo.get_all()

    def get_by_id(self, author_id: str) -> Optional[Author]:
        return self.repo.get_by_id(author_id)

    def create(self, name: str, surname: str, date_of_birth: str) -> Author:
        author_id = str(uuid.uuid4())
        author = Author(id=author_id, name=name, surname=surname, date_of_birth=date_of_birth)
        self.repo.save(author)
        return author

    def update(self, author_id: str, name: str, surname: str, date_of_birth: str) -> Author:
        author = self.repo.get_by_id(author_id)
        if not author:
            raise ValueError(f"Author with id {author_id} not found.")
        
        author.name = name
        author.surname = surname
        author.date_of_birth = date_of_birth
        self.repo.update(author)
        return author

    def delete(self, author_id: str) -> None:
        self.repo.delete(author_id)


class BookService:
    def __init__(self, book_repo: IBookRepository, author_repo: IAuthorRepository):
        self.book_repo = book_repo
        self.author_repo = author_repo

    def get_all(self) -> List[Book]:
        return self.book_repo.get_all()

    def get_by_id(self, book_id: str) -> Optional[Book]:
        return self.book_repo.get_by_id(book_id)

    def create(self, title: str, published_year: int, author_id: str) -> Book:
        author = self.author_repo.get_by_id(author_id)
        if not author:
            raise ValueError(f"Author with id {author_id} not found.")
        
        book_id = str(uuid.uuid4())
        book = Book(id=book_id, title=title, published_year=published_year, author=author)
        self.book_repo.save(book)
        return book

    def update(self, book_id: str, title: str, published_year: int, author_id: str) -> Book:
        book = self.book_repo.get_by_id(book_id)
        if not book:
            raise ValueError(f"Book with id {book_id} not found.")
            
        author = self.author_repo.get_by_id(author_id)
        if not author:
            raise ValueError(f"Author with id {author_id} not found.")
        
        book.title = title
        book.published_year = published_year
        book.author = author
        self.book_repo.update(book)
        return book

    def delete(self, book_id: str) -> None:
        self.book_repo.delete(book_id)