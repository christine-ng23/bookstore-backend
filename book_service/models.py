## book_service/models.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from common.models import Base, User

# Base = declarative_base()
# class User(Base):
#     __tablename__ = 'users'
#     id = Column(Integer, primary_key=True)
#     username = Column(String, unique=True, nullable=False)
#     password = Column(String, nullable=False)
#     role = Column(String, default='user')

class Book(Base):
    __tablename__ = 'books'
    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    publisher = Column(String)
    quantity = Column(Integer)
    imported_price = Column(Float)
    sell_price = Column(Float)

    def to_dict(self):
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "publisher": self.publisher,
            "quantity": self.quantity,
            "imported_price": self.imported_price,
            "sell_price": self.sell_price,
        }


class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    status = Column(String, default='new')
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    user = relationship("User")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "items": [item.to_dict() for item in self.items]
        }


class OrderItem(Base):
    __tablename__ = 'order_items'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    book_id = Column(Integer, ForeignKey('books.id'))
    quantity = Column(Integer)
    price_each = Column(Float)

    order = relationship("Order", back_populates="items")
    book = relationship("Book")

    def to_dict(self):
        return {
            "id": self.id,
            "order_id": self.order_id,
            "book_id": self.book_id,
            "quantity": self.quantity,
            "price_each": self.price_each
        }
