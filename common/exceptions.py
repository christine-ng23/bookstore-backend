class ForbiddenError(Exception):
    """Raised when the user is not allowed to perform the action"""
    pass

class RecordNotFoundError(Exception):
    """Raised when a database record is not found."""
    pass
