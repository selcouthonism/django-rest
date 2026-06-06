from .services import AuthorService, BookService
from .infrastructure import InMemoryAuthorRepository, InMemoryBookRepository

# Instantiate the DB adapter
author_repository = InMemoryAuthorRepository()
book_repository = InMemoryBookRepository()

# Inject the adapter into the service
author_service = AuthorService(repository=author_repository)
book_service = BookService(book_repo=book_repository, author_repo=author_repository)

def get_author_service() -> AuthorService:
    return author_service

def get_book_service() -> BookService:
    return book_service