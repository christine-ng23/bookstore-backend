### book_service/services/book_service.py
from sqlalchemy.orm import Session
from ..models import Book

def list_books(session: Session):
    return session.query(Book).all()

def get_book(session: Session, book_id: int):
    return session.query(Book).filter(Book.id == book_id).first()

def add_book(session: Session, data: dict):
    book = Book(**data)
    book.sell_price = round(book.imported_price * 1.1, 2)
    session.add(book)
    session.commit()
    return book

def update_book(session: Session, book_id: int, updates: dict):
    book = session.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise ValueError(f"Book with id {book_id} not found")
    for k, v in updates.items():
        setattr(book, k, v)
    if "imported_price" in updates:
        book.sell_price = round(book.imported_price * 1.1, 2)
    session.commit()
    return book

def delete_book(session: Session, book_id: int):
    book = session.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise ValueError(f"Book with id {book_id} not found")
    session.delete(book)
    session.commit()
    return book
