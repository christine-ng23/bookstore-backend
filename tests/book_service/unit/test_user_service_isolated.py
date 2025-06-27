## tests/book_service/integration/test_user_service.py
import pytest

from book_service.services.user_service import register_user, list_users, get_user_by_username, update_user, delete_user
from common.exceptions import ForbiddenError, RecordNotFoundError


@pytest.mark.parametrize("mock_session", [{"json_file": "test_seed_only_users.json"}], indirect=True)
def test_list_user(mock_session):
    users = list_users(mock_session)
    assert isinstance(users, list)
    assert len(users) == 2


def test_list_user_empty(mock_session):
    users = list_users(mock_session)
    assert users == []


def test_user_register_successful_with_admin_role_by_admin(mock_session):
    user_data = {"username": "admin_role", "password": "pw", "role": "admin"}
    user = register_user(mock_session, user_data, True)
    # Verify user data
    for attr in user_data:
        if attr == "password":
            assert user.verify_password(user_data[attr])
        else:
            assert getattr(user, attr) == user_data[attr]
    # Verify the database
    user = get_user_by_username(mock_session, user.username)
    assert user


def test_user_register_successful_with_user_role_by_user(mock_session):
    user_data = {"username": "user_role", "password": "pw", "role": "user"}
    user = register_user(mock_session, user_data, False)
    # Verify user data
    for attr in user_data:
        if attr == "password":
            assert user.verify_password(user_data[attr])
        else:
            assert getattr(user, attr) == user_data[attr]
    # Verify the database
    user = get_user_by_username(mock_session, user.username)
    assert user


def test_user_register_successful_with_default_user_role(mock_session):
    user_data = {"username": "user_role", "password": "pw"}
    user = register_user(mock_session, user_data, False)
    assert user.role == "user"


def test_user_register_successful_with_password_has_special_character(mock_session):
    user = register_user(mock_session, {"username": "abc", "password": "!@#$%^&*()"})
    special_char_passwords = [
        "admin<script>",
        "user!@#$%",
        "' OR '1'='1",
        "user with space",
        "💣🔥💥",
        "username_that_is_far_too_long_" + "x" * 300
    ]
    for i, password in enumerate(special_char_passwords):
        user = register_user(mock_session, {"username": f"user{i}", "password": password}, False)
        assert user.verify_password(password)


def test_user_register_unsuccessful_missing_required_fields(mock_session):
    user_data = {}
    with pytest.raises(ValueError, match="Missing required field: username; Missing required field: password"):
        register_user(mock_session, user_data, False)


def test_user_register_unsuccessful_invalid_field_types(mock_session):
    user_data = {"username": 1,
        "password": 2,
        "role": 3}
    with pytest.raises(ValueError, match="Field 'username' must be of type str; Field 'password' must be of type str; Field 'role' must be of type str"):
        register_user(mock_session, user_data, False)


def test_user_register_username_format_invalid(mock_session):
    bad_usernames = [
        "admin<script>",
        "user!@#$%",
        "' OR '1'='1",
        "user with space",
        "💣🔥💥"
    ]
    for username in bad_usernames:
        with pytest.raises(ValueError, match="Username format is invalid. Only letters, numbers, underscores, hyphens, and dots are allowed."):
            register_user(mock_session, {"username": username, "password": "pw"}, False)


def test_register_user_unsuccessful_role_value_invalid(mock_session):
    with pytest.raises(ValueError, match="Role must be one of: admin, user"):
        register_user(mock_session, {"username": "123", "password": "pw", "role": "test"}, False)


@pytest.mark.parametrize("mock_session", [{"json_file": "test_seed_only_users.json"}], indirect=True)
def test_user_register_unsuccessful_with_with_admin_role_by_user(mock_session):
    with pytest.raises(ForbiddenError, match="Only admin can assign roles other than 'user'"):
        register_user(mock_session, {"username": "user", "password": "pw2", "role": "admin"}, False)


@pytest.mark.parametrize("mock_session", [{"json_file": "test_seed_only_users.json"}], indirect=True)
def test_get_user_by_username(mock_session):
    user = get_user_by_username(mock_session, "user")
    assert user.username == "user"


def test_get_user_by_username_unsuccessful_not_existed(mock_session):
    username = "not_existed"
    with pytest.raises(RecordNotFoundError, match=f"User with username {username} not found"):
        get_user_by_username(mock_session, username)


@pytest.mark.parametrize("mock_session", [{"json_file": "test_seed_only_users.json"}], indirect=True)
def test_update_user_successful(mock_session):
    user_id = 1
    updates = {"username": "change", "password": "pw"}
    user = update_user(mock_session, user_id, updates)
    assert user.verify_password(updates["password"])


def test_update_user_non_exist(mock_session):
    user_id = 99
    with pytest.raises(RecordNotFoundError, match=f"User with id {user_id} not found"):
        update_user(mock_session, 99, {})


@pytest.mark.parametrize("mock_session", [{"json_file": "test_seed_only_users.json"}], indirect=True)
def test_update_user_violate_non_empty_if_present_fields(mock_session):
    updates = {"password": ""}
    with pytest.raises(ValueError, match=f"Missing required field: password"):
        update_user(mock_session, 1, updates)


@pytest.mark.parametrize("mock_session", [{"json_file": "test_seed_only_users.json"}], indirect=True)
def test_update_user_violate_field_types(mock_session):
    updates = {"password": 123}
    with pytest.raises(ValueError, match=f"Field 'password' must be of type str"):
        update_user(mock_session, 1, updates)


@pytest.mark.parametrize("mock_session", [{"json_file": "test_seed_only_users.json"}], indirect=True)
def test_delete_user_successful(mock_session):
    user= {"id": 2, "username": "user"}
    delete_user(mock_session, user["id"])
    with pytest.raises(RecordNotFoundError, match=f"User with username {user['username']} not found"):
        get_user_by_username(mock_session, user["username"])


def test_delete_user_unsuccessful_non_exist_user_id(mock_session):
    user_id = 1
    with pytest.raises(RecordNotFoundError, match=f"User with id {user_id} not found"):
        delete_user(mock_session, user_id)
