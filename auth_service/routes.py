## auth_service/routes.py

from flask import Blueprint, request, jsonify, current_app

from book_service.utils.utils import validate_field_types
from .init_admin import Session
from .token_utils import generate_token
from auth_service.config import CLIENT_ID, CLIENT_SECRET, TOKEN_EXPIRE_MINUTES
from common.models import User
import secrets

auth_bp = Blueprint('auth', __name__)
auth_codes = {}  # store temporary authorization codes


def get_session():
    session_factory = current_app.config.get("SESSION_FACTORY")
    return session_factory() if session_factory else Session()


@auth_bp.route('/authorize', methods=['POST'])
def authorize():
    # Validate required fields
    username = request.form.get('username')
    password = request.form.get('password')

    missing = []
    if not username:
        missing.append("username")
    if not password:
        missing.append("password")

    if missing:
        return jsonify({"error": "Missing required fields", "fields": missing}), 400

    redirect_uri = request.form.get('redirect_uri')

    with get_session() as session:
        user = session.query(User).filter_by(username=username).first()
        if not user or not user.verify_password(password):
            return jsonify({'error': 'Invalid username or password'}), 401

        # Simulate creating auth code
        code = secrets.token_urlsafe(16)
        print(code)
        auth_codes[code] = user.username

        # Redirect with code (normally you'd use HTTP redirect, here we simulate JSON)
        return jsonify({
            'redirect_uri': f'{redirect_uri}',
            'code': f'{code}'
        }), 200


@auth_bp.route('/token', methods=['POST'])
def exchange_token():
    data = request.get_json()
    client_id = data.get('client_id')
    client_secret = data.get('client_secret')
    for f in data:
        print(f"{f}={data[f]} (type: {type(data[f])})")
    code = data.get('code')
    redirect_uri = data.get('redirect_uri')
    print(data)
    # Validate required fields
    missing = []
    if not client_id:
        missing.append("client_id")
    if not client_secret:
        missing.append("client_secret")
    if not code:
        missing.append("code")

    if missing:
        return jsonify({"error": "Missing required fields", "fields": missing}), 400


    # Validate field types
    errors = []
    validate_field_types(data, {"client_id": str, "client_secret": str, "code": str}, errors)
    if errors:
        return jsonify({"error": "; ".join(errors)}), 400

    # Client verification
    if client_id != CLIENT_ID or client_secret != CLIENT_SECRET:
        return jsonify({'error': 'Invalid client'}), 401

    # Validate code
    if code not in auth_codes:
        return jsonify({'error': 'Invalid grant'}), 401

    username = auth_codes.pop(code)  # remove once used

    # if not redirect_uri.startswith("http://localhost"):
    #     return jsonify({'error': 'invalid_redirect_uri'}), 400

    # Get user role
    user = None
    with get_session() as session:
        user = session.query(User).filter_by(username=username).first()
        if not user:
            return jsonify({"error": "Forbidden: insufficient permission"}), 403

    # Issue access token
    payload = {
        "user_id": user.id,
        "role": user.role
    }
    access_token = generate_token(payload)
    print(access_token)

    return jsonify({
        'access_token': access_token,
        'token_type': 'bearer',
        'expires_in': TOKEN_EXPIRE_MINUTES,
        'redirect_uri': redirect_uri
    }), 200
