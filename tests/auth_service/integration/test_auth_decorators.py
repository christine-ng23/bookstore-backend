## auth_service/tests/integration/test_auth_decorators.py
import pytest
from flask import Flask, g, jsonify

from auth_service.auth_middleware import require_auth, require_role


@pytest.fixture
def app():
    app = Flask(__name__)

    @app.route("/protected")
    @require_auth()
    def secure():
        return jsonify({"message": "authorized"})

    @app.route("/admin")
    @require_auth()
    @require_role("admin")
    def admin():
        return jsonify({"message": "admin only"}), 200

    @app.route("/optional")
    @require_auth(optional=True)
    def optional():
        if g.user:
            return jsonify({"message": "authorized"}), 200
        else:
            return jsonify({"message": "unauthorized"}), 200

    return app


@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client


def test_require_auth_success(client, user_auth_header):
    res = client.get("/protected", headers=user_auth_header)
    assert res.status_code == 200
    assert res.json == {"message": "authorized"}


def test_require_auth_unsuccessful_missing_header(client):
    res = client.get("/protected")
    assert res.status_code == 401
    assert res.json == {"error": "Authorization header missing or invalid"}


def test_require_auth_unsuccessful_not_bear_header(client, auth_header_not_bear):
    res = client.get("/protected", headers=auth_header_not_bear)
    assert res.status_code == 401
    assert res.json == {"error": "Authorization header missing or invalid"}


def test_require_auth_unsuccessful_emtpy_token(client, auth_header_empty_token):
    res = client.get("/protected", headers=auth_header_empty_token)
    assert res.status_code == 401
    assert res.json == {"error": "Invalid token"}


def test_require_auth_invalid_token(client, auth_header_invalid_token):
    res = client.get("/protected", headers=auth_header_invalid_token)
    assert res.status_code == 401
    assert res.json == {"error": "Invalid token"}


def test_require_auth_expired_token(client, user_auth_header_expired):
    res = client.get("/protected", headers=user_auth_header_expired)
    assert res.status_code == 401
    assert res.json == {"error": "Token expired"}


def test_require_auth_unsuccessful_invalid_payload_missing_role(client, auth_header_payload_missing_role):
    res = client.get("/protected", headers=auth_header_payload_missing_role)
    assert res.status_code == 401
    assert res.json == {"error": "Invalid token payload: missing 'role'"}


def test_require_auth_unsuccessful_invalid_payload_missing_user_id(client, auth_header_payload_missing_user_id):
    res = client.get("/protected", headers=auth_header_payload_missing_user_id)
    assert res.status_code == 401
    assert res.json == {"error": "Invalid token payload: missing 'user_id'"}


def test_require_auth_optional_authorized(client, user_auth_header):
    res = client.get("/optional", headers=user_auth_header)
    assert res.status_code == 200
    assert res.json == {"message": "authorized"}


def test_require_auth_optional_missing_header(client):
    res = client.get("/optional")
    assert res.status_code == 200
    assert res.json == {"message": "unauthorized"}


def test_require_auth_optional_not_bear_header(client, auth_header_not_bear):
    res = client.get("/optional", headers=auth_header_not_bear)
    assert res.status_code == 200
    assert res.json == {"message": "unauthorized"}


def test_require_auth_optional_emtpy_token(client, auth_header_empty_token):
    res = client.get("/optional", headers=auth_header_empty_token)
    assert res.status_code == 200
    assert res.json == {"message": "unauthorized"}


def test_require_auth_optional_invalid_token(client, auth_header_invalid_token):
    res = client.get("/optional", headers=auth_header_invalid_token)
    assert res.status_code == 200
    assert res.json == {"message": "unauthorized"}


def test_require_auth_optional_expired_token(client, user_auth_header_expired):
    res = client.get("/optional", headers=user_auth_header_expired)
    assert res.status_code == 200
    assert res.json == {"message": "unauthorized"}


def test_require_auth_optional_invalid_payload_missing_role(client, auth_header_payload_missing_role):
    res = client.get("/optional", headers=auth_header_payload_missing_role)
    assert res.status_code == 200
    assert res.json == {"message": "unauthorized"}


def test_require_auth_optional_invalid_payload_missing_user_id(client, auth_header_payload_missing_user_id):
    res = client.get("/optional", headers=auth_header_payload_missing_user_id)
    assert res.status_code == 200
    assert res.json == {"message": "unauthorized"}

def test_require_role_success(client, admin_auth_header):
    res = client.get("/admin", headers=admin_auth_header)
    assert res.status_code == 200
    assert res.json == {"message": "admin only"}


def test_require_role_unsuccessful_forbidden(client, user_auth_header):
    res = client.get("/admin", headers=user_auth_header)
    assert res.status_code == 403
    assert res.json == {"error": "Forbidden: insufficient permission"}
