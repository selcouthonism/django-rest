from .services import BookService
from .infrastructure import InMemoryBookRepository

# Instantiate the DB adapter
book_repository = InMemoryBookRepository()

# Inject the adapter into the service
book_service = BookService(repository=book_repository)

def get_book_service() -> BookService:
    return book_service