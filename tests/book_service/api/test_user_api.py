## tests/book_service/api/test_user_api.py
import pytest

from common.constants import TEST_SESSION_TYPE
from common.utils import assert_json_structure


@pytest.mark.parametrize("client", [{"type": TEST_SESSION_TYPE, "json_file": "test_seed_only_users.json"}], indirect=True)
def test_list_users(client, admin_auth_header):
    """
    Response 200
        [
            {
                "id": 1,
                "role": "admin",
                "username": "admin"
            },..
        ]
    """
    res = client.get("/users", headers=admin_auth_header)
    assert res.status_code == 200
    assert isinstance(res.json, list)
    assert any("username" in user for user in res.json)


@pytest.mark.parametrize("client", [{"type": TEST_SESSION_TYPE}], indirect=True)
def test_list_user_unsuccessful_no_auth(client):
    """
    Response 401
        {
        "error": "Authorization header missing or invalid"
        }
    """
    res = client.get("/users")
    assert res.status_code == 401
    assert "error" in res.json
    assert res.json['error'] == "Authorization header missing or invalid"


@pytest.mark.parametrize("client", [{"type": TEST_SESSION_TYPE}], indirect=True)
def test_list_user_unsuccessful_not_bear_token(client, auth_header_not_bear):
    """
    Response 401
        {
        "error": "Authorization header missing or invalid"
        }
    """
    res = client.get("/users", headers=auth_header_not_bear)
    assert res.status_code == 401
    assert "error" in res.json
    assert res.json['error'] == "Authorization header missing or invalid"


@pytest.mark.parametrize("client", [{"type": TEST_SESSION_TYPE}], indirect=True)
def test_list_user_unsuccessful_empty_token(client, auth_header_empty_token):
    """
   Response 401
       {
       "error": "Authorization header missing or invalid"
       }
   """
    res = client.get("/users", headers=auth_header_empty_token)
    assert res.status_code == 401
    assert "error" in res.json
    assert res.json['error'] == "Authorization header missing or invalid"


@pytest.mark.parametrize("client", [{"type": TEST_SESSION_TYPE}], indirect=True)
def test_list_user_unsuccessful_invalid_token(client, auth_header_invalid_token):
    """
    Response 401
        {
            "error": "Invalid token"
        }
    """
    res = client.get("/users", headers=auth_header_invalid_token)
    assert res.status_code == 401
    assert "error" in res.json
    assert res.json['error'] == "Invalid token"


@pytest.mark.parametrize("client", [{"type": TEST_SESSION_TYPE}], indirect=True)
def test_list_user_unsuccessful_expired_token(client, user_auth_header_expired):
    """
    Response 401
        {
            "error": "Token expired"
        }
    """
    res = client.get("/users", headers=user_auth_header_expired)
    assert res.status_code == 401
    assert "error" in res.json
    assert res.json['error'] == "Token expired"


@pytest.mark.parametrize("client", [{"type": TEST_SESSION_TYPE}], indirect=True)
def test_list_users_unsuccessful_unauthorized(client, user_auth_header):
    """
    Response 403
        {
            "error": "Forbidden: insufficient permission"
        }
    """
    res = client.get("/users", headers=user_auth_header)
    assert res.status_code == 403
    assert "error" in res.json
    assert res.json['error'] == "Forbidden: insufficient permission"


@pytest.mark.parametrize("client", [{"type": TEST_SESSION_TYPE}], indirect=True)
def test_register_user_successful_with_admin_role_by_admin(client, admin_auth_header):
    """
    Response 201
        {
            "message": "User registered successfully",
            "user": {
                "id": <id>,
                "role": "admin",
                "username": "test_admin_1"
            }
        }
    """
    new_user = {
        "username": "admin_role",
        "password": "pw",
        "role": "admin"
    }
    res = client.post(
        "/users",
        json=new_user,
        headers=admin_auth_header
    )
    assert res.status_code == 201
    assert "user" in res.json
    user_info = res.json["user"]
    assert all(f in user_info for f in ["username", "role", "id"])
    assert all(user_info[f] == new_user[f] for f in ["username", "role"])


@pytest.mark.parametrize("client", [{"type": TEST_SESSION_TYPE}], indirect=True)
def test_register_user_successful_with_user_role_by_user(client, user_auth_header):
    """
    Response 201
    """
    new_user = {
        "username": "user_role",
        "password": "pw",
        "role": "user"
    }
    res = client.post(
        "/users",
        json=new_user,
        headers=user_auth_header
    )
    assert res.status_code == 201
    assert "user" in res.json
    user_info = res.json["user"]
    assert all(f in user_info for f in ["username", "role", "id"])
    assert all(user_info[f] == new_user[f] for f in ["username", "role"])


@pytest.mark.parametrize("client", [{"type": TEST_SESSION_TYPE}], indirect=True)
def test_register_user_successful_with_default_user_role_no_auth(client):
    """
    Response 201
    """
    new_user = {
        "username": "user_role",
        "password": "pw"
    }
    res = client.post(
        "/users",
        json=new_user
    )
    assert res.status_code == 201
    assert "user" in res.json
    user_info = res.json["user"]
    assert all(f in user_info for f in ["username", "role", "id"])
    assert user_info["username"] == new_user["username"]
    assert user_info["role"] == "user"


@pytest.mark.parametrize("client", [{"type": TEST_SESSION_TYPE}], indirect=True)
def test_register_user_unsuccessful_missing_json_body(client):
    """
    Response 415
        { "error": "Invalid or missing JSON in request body"}
    """
    res = client.post(
        "/users"
    )
    assert res.status_code == 415
    assert res.json["error"] == "Invalid or missing JSON in request body"


@pytest.mark.parametrize("client", [{"type": TEST_SESSION_TYPE}], indirect=True)
def test_register_user_unsuccessful_missing_required_fields(client):
    """
    Response 400
        {
            "error": "Missing required fields",
            "fields": [
                "username",
                "password"
            ]
        }
    """
    res = client.post(
        "/users",
        json={}
    )
    assert res.status_code == 400
    assert_json_structure(res.json, {"error": str, "fields": list})
    assert res.json["error"] == "Missing required fields"
    assert res.json["fields"] == ["username", "password"]


@pytest.mark.parametrize("client", [{"type": TEST_SESSION_TYPE}], indirect=True)
def test_register_user_unsuccessful_field_type_invalid(client, admin_auth_header):
    """
    Response 400
    {
        "error": "Field 'username' must be of type str; Field 'password' must be of type str; Field 'role' must be of type str"
    }
    """
    new_user = {
        "username": 1,
        "password": 2,
        "role": 3
    }
    res = client.post(
        "/users",
        json=new_user,
        headers=admin_auth_header
    )
    assert res.status_code == 400
    assert "error" in res.json and res.json["error"] == ("Field 'username' must be of type str; Field 'password' must"
                                                         " be of type str; Field 'role' must be of type str")


@pytest.mark.parametrize("client", [{"type": TEST_SESSION_TYPE}], indirect=True)
def test_register_user_unsuccessful_username_format_invalid(client, admin_auth_header):
    """
    Response 400
        {
            "error": "Username format is invalid. Only letters, numbers, underscores, hyphens, and dots are allowed."
        }
    """
    new_user = {
        "username": "invalid username!",
        "password": "securepass123"
    }
    res = client.post(
        "/users",
        json=new_user,
        headers=admin_auth_header
    )
    assert res.status_code == 400
    assert "error" in res.json and res.json["error"] == ("Username format is invalid. Only letters, numbers,"
                                                         " underscores, hyphens, and dots are allowed.")


@pytest.mark.parametrize("client", [{"type": TEST_SESSION_TYPE}], indirect=True)
def test_register_user_unsuccessful_role_value_invalid(client, admin_auth_header):
    """
    Response 400
        { "error": "Role must be one of: admin, user"}
    """
    new_user = {
        "username": "test_user_1",
        "password": "securepass123",
        "role": "user2"
    }
    res = client.post(
        "/users",
        json=new_user,
        headers=admin_auth_header
    )
    assert res.status_code == 400
    assert "error" in res.json
    assert res.json['error'] == "Role must be one of: admin, user"

@pytest.mark.parametrize("client", [{"type": TEST_SESSION_TYPE}], indirect=True)
def test_register_user_unsuccessful_with_admin_role_by_user(client, user_auth_header):
    """
    Response 403
        { "error": "Only admin can assign roles other than 'user'"}
    """
    new_user = {
        "username": "test_user_1",
        "password": "securepass123",
        "role": "admin"
    }
    res = client.post(
        "/users",
        json=new_user,
        headers=user_auth_header
    )
    assert res.status_code == 403
    assert "error" in res.json
    assert res.json['error'] == "Only admin can assign roles other than 'user'"


@pytest.mark.parametrize("client", [{"type": TEST_SESSION_TYPE, "json_file": "test_seed_only_users.json"}], indirect=True)
def test_register_user_not_unique_username(client):
    """
    Response 400
        { "error": "A user with this username already exists."}
    """
    new_user = {
        "username": "user",
        "password": "pw",
        "role": "user"
    }
    res = client.post(
        "/users",
        json=new_user
    )
    assert res.status_code == 400
    assert "error" in res.json
    assert res.json['error'] == "A user with this username already exists."
