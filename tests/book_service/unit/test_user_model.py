## book_service/tests/unit/test_user_model.py

from book_service.models import User


def test_user_model_fields():
    user = User(username="john", password="secret", role="admin")
    assert user.username == "john"
    assert user.password == "secret"
    assert user.role == "admin"


def test_user_to_dict():
    user = User(id=1, username="john", password="secret", role="user")
    user_dict = user.to_dict()
    assert user_dict == {"id": 1, "username": "john", "role": "user"}
