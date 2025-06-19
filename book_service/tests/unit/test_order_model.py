## book_service/tests/unit/test_order_model.py
from datetime import datetime, timezone

import pytest
from sqlalchemy.exc import IntegrityError

from book_service.models import Order, Book, OrderItem
from common.models import User


def test_order_model_fields():
    order = Order(id=1, user_id=2, status="new", created_at=datetime.now(timezone.utc))
    assert order.id == 1
    assert order.user_id == 2
    assert order.status == "new"


def test_order_to_dict():
    order = Order(id=1, user_id=2, status="new", created_at=datetime(2024, 1, 1))
    order_dict = order.to_dict()
    assert order_dict == {'id': 1,
                          'status': 'new',
                          'user_id': 2,
                          'items': [],
                          'created_at': '2024-01-01T00:00:00'}


def test_order_with_items_to_dict():
    order = Order(id=1, user_id=2, status="new", created_at=datetime(2024, 1, 1))
    item = OrderItem(order_id=3, book_id=4, quantity=5, price_each=30.5)
    order.items.append(item)
    order_dict = order.to_dict()
    assert order_dict == {'created_at': '2024-01-01T00:00:00',
                          'id': 1,
                          'user_id': 2,
                          'status': 'new',
                          'items': [{'book_id': 4,
                                     'id': None,
                                     'order_id': 3,
                                     'price_each': 30.5,
                                     'quantity': 5}]}


def test_foreign_key_relationship(db_session):
    # Create required parent records
    user = User(username="testuser", password="hashed", role="user")
    book = Book(code="B100", name="SQLAlchemy Book", publisher="Pub", quantity=5, imported_price=80, sell_price=88)
    db_session.add(user)
    db_session.add(book)
    db_session.commit()

    # Create order with valid FK with one-one relationship
    order = Order(user_id=user.id, status="new", created_at=datetime.utcnow())
    db_session.add(order)
    db_session.commit()
    assert order.user == user

    # Create order with one-many relationship
    item = OrderItem(order_id=order.id, book_id=book.id, quantity=1, price_each=88)
    db_session.add(item)
    db_session.commit()
    assert len(order.items) == 1 and order.items[0] == item


def test_foreign_key_enforcement(db_session):
    # Create required parent records
    user = User(username="testuser", password="hashed", role="user")
    db_session.add(user)
    db_session.commit()

    # Attempt to break FK
    order = Order(user_id=999, status="new", created_at=datetime.now())
    db_session.add(order)
    with pytest.raises(IntegrityError):
        db_session.commit()
