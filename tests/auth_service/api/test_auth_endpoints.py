## tests/auth_service/api/test_auth_endpoints.py
import pytest

from auth_service.config import CLIENT_ID, CLIENT_SECRET


@pytest.mark.parametrize("auth_api", [{"json_file": "test_seed_only_users.json"}], indirect=True)
def test_authorize_successful(auth_api, user):
    res = auth_api.authorize({"username": user["username"], "password": user["password"]})
    assert res.status_code == 200
    assert res.json()["code"]


def test_authorize_unsuccessful_missing_required_fields(auth_api):
    res = auth_api.authorize({})
    assert res.status_code == 400
    assert res.json() == {
        "error": "Missing required fields",
        "fields": [
            "username",
            "password"
        ]
    }


@pytest.mark.parametrize("auth_api", [{"json_file": "test_seed_only_users.json"}], indirect=True)
def test_authorize_unsuccessful_non_existed_username(auth_api):
    res = auth_api.authorize({"username": "non-exsited", "password": "pw"})
    assert res.status_code == 401
    assert res.json() == {
        "error": "Invalid username or password"
    }


@pytest.mark.parametrize("auth_api", [{"json_file": "test_seed_only_users.json"}], indirect=True)
def test_authorize_unsuccessful_incorrect_password(auth_api, user):
    res = auth_api.authorize({"username": user["username"], "password": "incorrect"})
    assert res.status_code == 401
    assert res.json() == {
        "error": "Invalid username or password"
    }


@pytest.mark.parametrize("auth_api", [{"json_file": "test_seed_only_users.json"}], indirect=True)
def test_exchange_token_successful(auth_api, code):
    res_token = auth_api.exchange_token(json={
        "client_id": f"{CLIENT_ID}",
        "client_secret": f"{CLIENT_SECRET}",
        "code": f"{code}"
    })

    assert res_token.status_code == 200
    json_data = res_token.json()
    assert "access_token" in json_data
    assert "expires_in" in json_data
    assert json_data.get("role", "") == "admin"

def test_exchange_token_unsuccessful_missing_required_field(auth_api):
    res = auth_api.exchange_token(json={})
    assert res.status_code == 400
    assert res.json() == {
        "error": "Missing required fields",
        "fields": [
            "client_id",
            "client_secret",
            "code"
        ]
    }

def test_exchange_token_unsuccessful_incorrect_field_types(auth_api):
    res = auth_api.exchange_token(json={
        "client_id": 1,
        "client_secret": 2,
        "code": 3
    })
    assert res.status_code == 400
    assert res.json() == {
        "error": "Field 'client_id' must be of type str; Field 'client_secret' must "
          "be of type str; Field 'code' must be of type str"
    }


@pytest.mark.parametrize("auth_api", [{"json_file": "test_seed_only_users.json"}], indirect=True)
def test_exchange_token_unsuccessful_invalid_client_id(auth_api, code):
    res = auth_api.exchange_token(json={
        "client_id": f"invalid_id",
        "client_secret": f"{CLIENT_SECRET}",
        "code": f"{code}"})
    assert res.status_code == 401
    assert res.json() == {
        "error": "Invalid client"
    }


@pytest.mark.parametrize("auth_api", [{"json_file": "test_seed_only_users.json"}], indirect=True)
def test_exchange_token_unsuccessful_invalid_client_id_secret(auth_api, code):
    res = auth_api.exchange_token(json={
        "client_id": f"{CLIENT_ID}",
        "client_secret": "secret",
        "code": f"{code}"})
    assert res.status_code == 401
    assert res.json() == {
        "error": "Invalid client"
    }
def test_exchange_token_unsuccessful_invalid_code(auth_api):
    res = auth_api.exchange_token(json={
        "client_id": f"{CLIENT_ID}",
        "client_secret": f"{CLIENT_SECRET}",
        "code": f"invalid_code"})
    assert res.status_code == 401
    assert res.json() == {
        "error": "Invalid grant"
    }
