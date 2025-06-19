## auth_service/tests/integration/test_auth_service.py
import pytest
from flask import Flask

from auth_service.token_utils import generate_token
from auth_service.auth_middleware import require_auth, require_role
import jwt
from auth_service.config import SECRET
from datetime import datetime, timedelta, timezone
from pytest_check import check


@pytest.fixture
def app():
    app = Flask(__name__)

    @app.route("/protected")
    @require_auth
    def secure():
        return "authorized"

    @app.route("/admin")
    @require_auth
    @require_role("admin")
    def admin():
        return "admin only"

    return app

@pytest.fixture
def client(app):
    return app.test_client()

def make_auth_header(token):
    return {"Authorization": f"Bearer {token}"}

def generate_tokens(role):
    data_for_auth_code = {"username": "username", "password": "password", "redirect_uri": "some_uri"}
    data_for_token = {
        "client_id": "client123",
        "client_secret": "secret456",
        "redirect_uri": "/books",
        "code": "R__YYI-advHzfskzngjTug"
    }
    payload = {"user_id": 1, "role": role, "exp": datetime.now(timezone.utc) + timedelta(minutes=1)}
    return jwt.encode(payload, SECRET, algorithm="HS256")

def test_require_auth_success(client):
    # token = generate_token({"user_id": 1, "role":"user"})
    token = generate_token({"user_id": 1, "role":"user"})
    res = client.get("/protected", headers=make_auth_header(token))
    check.equal(res.status_code, 200)
    check.equal(res.data, b"authorized")

def test_require_auth_missing_header(client):
    res = client.get("/protected")
    assert res.status_code == 401
    assert "Authorization header missing or invalid" == res.json["error"]

def test_require_auth_malformed_header(client):
    res = client.get("/protected", headers={"Authorization": "Token xxxxx"})
    assert res.status_code == 401
    assert "Authorization header missing or invalid" == res.json["error"]

def test_require_auth_invalid_token(client):
    res = client.get("/protected", headers=make_auth_header("not-a-token"))
    assert res.status_code == 401
    assert "Invalid token" == res.json["error"]

def test_require_auth_invalid_token_format_user_id(client):
    token = generate_token({"role":"user"})
    res = client.get("/protected", headers=make_auth_header(token))
    assert res.status_code == 401
    assert "Invalid token" == res.json["error"]

def test_require_auth_invalid_token_format_role(client):
    token = generate_token({"user_id": "1"})
    res = client.get("/protected", headers=make_auth_header(token))
    assert res.status_code == 401
    assert "Invalid token" == res.json["error"]

def test_require_auth_expired_token(client):
    expired_token = jwt.encode(
        {"user_id": 1, "role": "user", "exp": datetime.now(timezone.utc) - timedelta(seconds=1)},
        SECRET, algorithm="HS256"
    )

    res = client.get("/protected", headers=make_auth_header(expired_token))
    assert res.status_code == 401
    assert "Token expired" in res.json["error"]

def test_require_role_success(client):
    token = generate_token({"user_id":1, "role":"admin"})
    res = client.get("/admin", headers=make_auth_header(token))
    assert res.status_code == 200
    assert b"admin only" in res.data

def test_require_role_forbidden(client):
    token = generate_token({"user_id":1, "role":"user"})
    res = client.get("/admin", headers=make_auth_header(token))
    assert res.status_code == 403
    assert res.json["error"] == "Forbidden: insufficient permission"

def test_require_role_missing_header(client):
    res = client.get("/admin")
    assert res.status_code == 401
    assert res.json["error"] == "Authorization header missing or invalid"

def test_require_role_malformed_token(client):
    res = client.get("/admin", headers={"Authorization": "Bearer abc.def.ghi"})
    assert res.status_code == 401
    assert res.json["error"] == "Invalid token"

def test_require_role_expired_token(client):
    expired_token = jwt.encode(
        {"user_id": 1, "role": "admin", "exp": datetime.utcnow() - timedelta(minutes=1)},
        SECRET, algorithm="HS256"
    )
    res = client.get("/admin", headers=make_auth_header(expired_token))
    assert res.status_code == 401
    assert "Token expired" in res.json["error"]
