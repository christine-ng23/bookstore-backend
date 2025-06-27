## book_service/tests/unit/test_book_model.py

import pytest
from sqlalchemy.exc import IntegrityError

from book_service.models import Book


def test_book_model_fields():
    book = Book(code="B001", name="Book", publisher="Pub", quantity=5, imported_price=100.0, sell_price=110.0)
    assert book.name == "Book"
    assert book.code == "B001"
    assert book.publisher == "Pub"
    assert book.quantity == 5
    assert book.imported_price == 100
    assert book.sell_price == 110.0


def test_book_to_dict():
    book = Book(id=1, code="B001", name="Book", publisher="Pub", quantity=5, imported_price=100.0, sell_price=110.0)
    book_dict = book.to_dict()
    assert book_dict["id"] == 1
    assert book_dict["code"] == "B001"
    assert book_dict["name"] == "Book"
    assert book_dict["publisher"] == "Pub"
    assert book_dict["quantity"] == 5
    assert book_dict["imported_price"] == 100
    assert book_dict["sell_price"] == 110


def test_book_blank_code(db_session):
    with pytest.raises(IntegrityError):
        book = Book(name="Invalid Book", publisher="BadPub", quantity=1, imported_price=50, sell_price=55)
        db_session.add(book)
        db_session.commit()


def test_book_blank_name(db_session):
    with pytest.raises(IntegrityError):
        book = Book(code="B002", publisher="BadPub", quantity=1, imported_price=50, sell_price=55)
        db_session.add(book)
        db_session.commit()
