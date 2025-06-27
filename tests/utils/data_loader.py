import json
import os

from book_service.models import OrderItem, Order, Book
from common.auth import hash_password
from common.constants import TEST_DATA_DIR
from common.models import User, Base


def clean_data(session):
    for table in reversed(Base.metadata.sorted_tables):
        session.execute(table.delete())
        session.commit()
    # session.query(OrderItem).delete()
    # session.query(Order).delete()
    # session.query(Book).delete()
    # session.query(User).delete()
    session.commit()


def initialized_data(session, json_file):
    json_path = os.path.join(TEST_DATA_DIR, json_file)
    with open(json_path) as f:
        data = json.load(f)

    # Users
    username_map = {}
    for user in data.get("users", []):
        new_user = User(
            username=user["username"],
            password=hash_password(user["password"]),
            role=user["role"]
        )
        session.add(new_user)
        session.flush()
        username_map[user["username"]] = new_user.id

    # Books
    book_map = {}
    for book in data.get("books", []):
        new_book = Book(**book)
        session.add(new_book)
        session.flush()
        book_map[book["code"]] = new_book.id

    # Orders and Items
    for order in data.get("orders", []):
        user_id = username_map[order["user_username"]]
        new_order = Order(user_id=user_id, status=order["status"])
        session.add(new_order)
        session.flush()

        for item in order["items"]:
            book_id = book_map[item["book_code"]]
            order_item = OrderItem(
                order_id=new_order.id,
                book_id=book_id,
                quantity=item["quantity"],
                price_each=item["price_each"]
            )
            session.add(order_item)

    session.commit()
