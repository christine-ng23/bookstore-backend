### book_service/services/book_service.py
"""
Book Service Layer

Provides core logic for managing books, including listing, creation, updates, and deletion.

Responsibilities:
    - Validate input types (e.g., title as string, price as float)
    - Check for required fields in create/update scenarios
    - Enforce business rules (e.g., price must be non-negative, code must be unique)
    - Raise clear and consistent exceptions (ValueError, ForbiddenError) for the route layer to handle
    - Interact with the book database model for persistence and queries
    - Validation order: input type (-> record existence) -> required/non-empty+type+non-negative (business rule)
        -> DB checks
    - Uses @validate_types to validate input types and raise ValueError on first error
"""
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from common.exceptions import RecordNotFoundError
from ..models import Book
from ..utils.handlers import validate_types
from ..utils.utils import validate_required_fields, validate_field_types, validate_non_negative_fields, \
    validate_non_empty_if_present, filter_valid_model_fields


def validate_book_data(data: dict, is_create: bool) -> None:
    """Validate book data for required fields and data types, raise ValueError on violations"""
    errors = []
    # Required or optional-but-present validation
    if is_create:
        validate_required_fields(data, ["code", "name"], errors)
    else:
        validate_non_empty_if_present(data, ["code", "name"], errors)

    # Type checking
    validate_field_types(data, {"code": str, "name": str, "quantity": int, "publisher": str,
                                "imported_price": (int, float), "sell_price": (int, float)}, errors)
    if errors:
        raise ValueError("; ".join(errors))

    # Non-negative numeric fields
    validate_non_negative_fields(data, ["quantity", "imported_price", "sell_price"], errors)
    if errors:
        raise ValueError("; ".join(errors))


def list_books(session: Session) -> list[Book]:
    """
    Get all books
    :param session: database session
    """
    return session.query(Book).all()


@validate_types(book_id=int)
def get_book(session: Session, book_id: int) -> None:
    """
    Get book by id
    :param session: database session
    :param book_id: book id
    :exception: TypeError: function input type error
        RecordNotFoundError: book_id is not found
    """
    book = session.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise RecordNotFoundError(f"Book with id {book_id} not found")


@validate_types(data=dict)
def add_book(session: Session, data: dict) -> Book:
    """
    Add a book
    :param session: database session
    :param data: dict of book data: { "code": "B001", "name": self.name, "publisher": self.publisher,
            "quantity": 20, "imported_price": 10.55, "sell_price": 11.95}
    :exception TypeError: function input type error
        ValueError: for violations on required fields, field types
            then, for violations on field values of non-negative fields
            then, for not-unique book code
        IntegrityError, raised by SessionTransaction for Unique constraint violation (primary_key, unique)
    """
    # Fields validation
    validate_book_data(data, is_create=True)

    # Filter for valid field names before update model object
    data = filter_valid_model_fields(Book, data)
    book = Book(**data)
    # Update sell_price according to imported_price
    if not data.get("sell_price") and data.get("imported_price"):
        book.sell_price = round(book.imported_price * 1.1, 2)
    session.add(book)
    try:
        session.commit()
    except IntegrityError as ie:
        session.rollback()
        if "UNIQUE constraint failed" in str(ie.orig):
            raise ValueError("A book with this code already exists.")
        raise
    return book


@validate_types(book_id=int, updates=dict)
def update_book(session: Session, book_id: int, updates: dict) -> Book:
    """
    Update a book by id
    :param session: database session
    :param book_id: book id
    :param updates: dict of book update data: { "name": "Book name"}
    :exception TypeError: function input type error
        ValueError: for violations on non-empty-if-present fields, field types
            then, for violations on field values of non-negative fields
            then, for not-unique book code
        IntegrityError, raised by SessionTransaction for Unique constraint violation (primary_key, unique)
    """
    book = session.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise RecordNotFoundError(f"Book with id {book_id} not found")

    # Fields validation
    validate_book_data(updates, is_create=False)

    # Fields update
    allowed_to_update_fields = ["code", "name", "publisher", "quantity", "imported_price", "sell_price"]
    for k in allowed_to_update_fields:
        if k in updates:
            setattr(book, k, updates[k])

    if updates.get("imported_price") and not updates.get("sell_price"):
        book.sell_price = round(book.imported_price * 1.1, 2)
    try:
        session.commit()
    except IntegrityError as ie:
        session.rollback()
        if "UNIQUE constraint failed" in str(ie.orig):
            raise ValueError("A book with this code already exists.")
        raise
    return book


@validate_types(book_id=int)
def delete_book(session: Session, book_id: int) -> Book:
    """
    Delete a book by id
    :param session: database session
    :param book_id: book id
    :exception: TypeError: function input type error
        RecordNotFoundError: book_id is not found
        IntegrityError: FK constraint violation
    """
    book = session.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise RecordNotFoundError(f"Book with id {book_id} not found")
    session.delete(book)
    session.commit()
    return book
