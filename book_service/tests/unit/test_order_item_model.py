## book_service/tests/unit/test_order_item_model.py
from datetime import datetime

import pytest
from sqlalchemy.exc import IntegrityError

from book_service.models import OrderItem, Book, Order
from common.models import User


def test_order_item_model_fields():
    item = OrderItem(id=1, order_id=1, book_id=2, quantity=3, price_each=100.0)
    assert item.order_id == 1
    assert item.book_id == 2
    assert item.quantity == 3
    assert item.price_each == 100.0


def test_order_item_to_dict():
    item = OrderItem(id=1, order_id=1, book_id=2, quantity=3, price_each=100.0)
    item_dict = item.to_dict()
    assert item_dict == {
        "id": 1,
        "order_id": 1,
        "book_id": 2,
        "quantity": 3,
        "price_each": 100.0
    }


def test_foreign_key_relationship(db_session):
    # Create required parent records
    user = User(username="testuser", password="hashed", role="user")
    book = Book(code="B100", name="SQLAlchemy Book", publisher="Pub", quantity=5, imported_price=80, sell_price=88)
    db_session.add(user)
    db_session.add(book)
    db_session.commit()

    # Create order
    order = Order(user_id=user.id, status="new", created_at=datetime.utcnow())
    db_session.add(order)
    db_session.commit()

    # Create order item with valid FK and many-one relationship
    item = OrderItem(order_id=order.id, book_id=book.id, quantity=1, price_each=88)
    db_session.add(item)
    db_session.commit()
    assert item.order == order
    assert item.book == book


def test_foreign_key_enforcement(db_session):
    # Create required parent records
    user = User(username="testuser", password="hashed", role="user")
    book = Book(code="B100", name="SQLAlchemy Book", publisher="Pub", quantity=5, imported_price=80, sell_price=88)
    db_session.add(user)
    db_session.add(book)
    db_session.commit()

    # Create order
    order = Order(user_id=user.id, status="new", created_at=datetime.utcnow())
    db_session.add(order)
    db_session.commit()

    # Attempt to break FK
    broken_item = OrderItem(order_id=999, book_id=book.id, quantity=1, price_each=88)
    db_session.add(broken_item)
    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()

    broken_item = OrderItem(order_id=order.id, book_id=999, quantity=1, price_each=88)
    db_session.add(broken_item)
    with pytest.raises(IntegrityError):
        db_session.commit()
