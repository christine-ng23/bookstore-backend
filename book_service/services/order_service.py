### book_service/services/order_service.py
"""
Order Service Layer

Handles all order-related business logic, including placing orders, updating status, and listing user orders.

Responsibilities:
    - Validate input types and required fields (e.g., book_id: int, quantity: int)
    - Enforce order status transition rules (e.g., NEW -> PROCESSING -> SHIPPING -> DELIVERED)
    - Apply role-based business logic:
        - Admins can update any orders, following allowed status transitions
        - Users can only cancel their own orders when status is NEW
    - Check ownership when performing order-specific actions
    - Raise domain-specific exceptions (ValueError, ForbiddenError)
    - Interact with book and order models for persistence and stock checking
    - Ensure transactional integrity (e.g., only place orders when enough stock)
    - Validation order: input type (-> record existence (order)) -> items non-empty -> book fields: required+type+non-negative
    -> record existence (book)-> stock (business rule) -> DB checks
    - Uses @validate_types to validate input types and raise ValueError on first error
"""


from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm import Session

from common.constants import ORDER_TRANSITIONS, OrderStatus
from common.exceptions import ForbiddenError, RecordNotFoundError
from ..models import Order, OrderItem, Book
from ..utils.handlers import validate_types
from ..utils.utils import validate_field_types, validate_required_fields, validate_non_negative_fields


@validate_types(user_id=int, items=list)
def place_order(session: Session, user_id: int, items: list) -> Order:
    """
    Create a new order
    :param session: database session
    :param user_id
    :param items: order items info: {"items": [{ "book_id": 1, "quantity": 3 }]}
    :exception: TypeError: function input type error
        ValueError: raise when error about empty items
            then, when error about status value is invalid
            then, when errors about items fields (book_id, quantity): required fields, field types, non-negative
        RecordNotFoundError: book_id is not existed
        ValueError: book quantity is not enough
    """

    order = Order(user_id=user_id, status=OrderStatus.NEW)
    session.add(order)
    session.flush()
    if not items:
        raise ValueError("Items can not empty")

    errors = []
    for item in items:
        # Validate the order item for field required, types, non-negative
        validate_required_fields(item, ["book_id", "quantity"], errors)
        validate_field_types(item, {"book_id": int, "quantity": int}, errors)
        if errors:
            raise ValueError("; ".join(errors))

        validate_non_negative_fields(item, ["book_id", "quantity"], errors)
        if errors:
            raise ValueError("; ".join(errors))

        # Validate the order item for exist book id, available stock
        book = session.query(Book).filter(Book.id == item['book_id']).first()
        if not book:
            raise RecordNotFoundError(f"Book with id {item['book_id']} not found")
        elif book.quantity < item['quantity']:
            raise ValueError(f"Book with id {item['book_id']} quantity not enough")

        book.quantity -= item['quantity']
        session.add(OrderItem(
            order_id=order.id,
            book_id=item['book_id'],
            quantity=item['quantity'],
            price_each=book.sell_price))

    session.commit()
    return order


@validate_types(user_id=(int, type(None)), is_admin=bool)
def list_orders(session: Session, user_id: int=None, is_admin: bool = False) -> list[Order]:
    """
    Get all orders if user is admin, or user own orders
    :param session: database session
    :param user_id
    :param is_admin
    :exception: TypeError: function input type error
    """
    if is_admin:
        return session.query(Order).all()
    return session.query(Order).filter(Order.user_id == user_id).all()


@validate_types(order_id=int, status=str, user_id=(int, type(None)), is_admin=bool)
def update_order_status(session: Session, order_id: int, status: str, user_id: int=None, is_admin: bool = False) -> Order:
    """
    Allow admin to update any order status, while normal user is only able to cancel their orders
    :param session: database session
    :param order_id
    :param user_id
    :param is_admin
    :param status: the new status must follow status transitions
    :exception: TypeError: function input type error
        RecordNotFoundError: order_id not found
        ValueError: status value is invalid
        ForbiddenError: status not follows status transitions
        InvalidRequestError: user does not have permission to update status
        IntegrityError: DB check violation (e.g., FK, constraints)
    """
    order = session.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise RecordNotFoundError(f"Order with id {order_id} not found")

    # Validate new status value
    if status not in OrderStatus.ALL:
        raise ValueError(f"status must be one of: {', '.join(sorted(OrderStatus.ALL))}")

    # Check for permission
    if not(is_admin or (order.user_id == user_id and status == OrderStatus.CANCELED and order.status == OrderStatus.NEW)):
        raise ForbiddenError("You are not authorized to update this order.")

    # Check if following allowed status transitions
    if is_admin:
        valid_next = ORDER_TRANSITIONS.get(order.status, [])
        if status not in valid_next:
            raise InvalidRequestError(f"Cannot change status from {order.status} to {status}")

    # Update order status
    order.status = status
    session.commit()
    return order
