
class BaseApplicationError(Exception):
    """Base class for all domain and application-level exceptions."""
    pass

class AuthenticationError(BaseApplicationError):
    """Raised when authentication or token verification fails."""
    pass

class ValidationError(BaseApplicationError):
    """Raised when input data is invalid."""
    pass