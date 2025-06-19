### book_service/services/order_service.py
from sqlalchemy.orm import Session
from ..models import Order, OrderItem, Book

def place_order(session: Session, user_id: int, items: list):
    order = Order(user_id=user_id, status='new')
    session.add(order)
    session.flush()

    for item in items:
        book = session.query(Book).filter(Book.id == item['book_id']).first()
        if not book or book.quantity < item['quantity']:
            continue
        book.quantity -= item['quantity']
        session.add(OrderItem(
            order_id=order.id,
            book_id=item['book_id'],
            quantity=item['quantity'],
            price_each=book.sell_price
        ))
    session.commit()
    return order

def list_orders(session: Session, user_id=None, is_admin=False):
    if is_admin:
        return session.query(Order).all()
    return session.query(Order).filter(Order.user_id == user_id).all()

def update_order_status(session: Session, order_id: int, status: str, user_id=None, is_admin=False):
    order = session.query(Order).filter(Order.id == order_id).first()
    if not order:
        return None
    if is_admin or (order.user_id == user_id and status == 'canceled' and order.status == 'new'):
        order.status = status
        session.commit()
        return order
    return None
