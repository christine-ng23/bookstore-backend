## auth_service/routes.py

from flask import Blueprint, request, jsonify
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from common.constants import DB_PATH
from .token_utils import generate_token
from auth_service.config import CLIENT_ID, CLIENT_SECRET
from common.models import User
import secrets

Session = sessionmaker(bind=create_engine(f'sqlite:///{DB_PATH}'))
auth_bp = Blueprint('auth', __name__)

auth_codes = {}  # store temporary authorization codes

@auth_bp.route('/authorize', methods=['POST'])
def authorize():
    username = request.form.get('username')
    password = request.form.get('password')

    errors = []
    if not username:
        errors.append("Username is required.")
    if not password:
        errors.append("Password is required.")

    if errors:
        return jsonify({"errors": errors}), 400  # Bad Request

    redirect_uri = request.form.get('redirect_uri')

    print(username, password, redirect_uri)
    with Session() as session:
        user = session.query(User).filter_by(username=username).first()
        print(user)
        if not user or not user.verify_password(password):
            return jsonify({'error': 'Invalid username or password'}), 401

        # Simulate creating auth code
        code = secrets.token_urlsafe(16)
        print(code)
        auth_codes[code] = user.username

        # Redirect with code (normally you'd use HTTP redirect, here we simulate JSON)
        return jsonify({
            'redirect_uri': f"{redirect_uri}?code={code}&state=xyz"
        }), 200


@auth_bp.route('/token', methods=['POST'])
def exchange_token():
    data = request.get_json()
    client_id = data.get('client_id')
    client_secret = data.get('client_secret')
    code = data.get('code')
    redirect_uri = data.get('redirect_uri')
    print(client_id, client_secret, code)
    # Simple client verification
    if client_id != CLIENT_ID or client_secret != CLIENT_SECRET:
        return jsonify({'error': 'invalid_client'}), 401

    # Validate code
    if code not in auth_codes:
        return jsonify({'error': 'invalid_grant'}), 400

    username = auth_codes.pop(code)  # remove once used

    # if not redirect_uri.startswith("http://localhost"):
    #     return jsonify({'error': 'invalid_redirect_uri'}), 400

    # Get user role
    user = None
    with Session() as session:
        user = session.query(User).filter_by(username=username).first()
        if not user:
            return jsonify({"error": "Forbidden: insufficient permission"}), 403

    # Issue access token
    payload = {
        "user_id": user.id,
        "role": user.role
    }
    access_token = generate_token(payload)

    return jsonify({
        'access_token': access_token,
        'token_type': 'bearer',
        'expires_in': 3600,
        'redirect_uri': redirect_uri
    }), 200

