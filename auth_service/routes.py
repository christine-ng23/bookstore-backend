## auth_service/routes.py

from flask import request, jsonify, current_app, make_response
from flask_restx import Namespace, Resource, fields

from book_service.utils.utils import validate_field_types
from .init_admin import Session
from .token_utils import generate_token
from auth_service.config import CLIENT_ID, CLIENT_SECRET, TOKEN_EXPIRE_MINUTES
from common.models import User
import secrets

auth_codes = {}  # store temporary authorization codes

auth_api_ns = Namespace('auth', path='/')

authorize_model = auth_api_ns.model('AuthorizeRequest', {
    'username': fields.String(required=True),
    'password': fields.String(required=True),
    'redirect_uri': fields.String()
})

token_model = auth_api_ns.model('TokenRequest', {
    'client_id': fields.String(required=True),
    'client_secret': fields.String(required=True),
    'code': fields.String(required=True)
})

def get_session():
    session_factory = current_app.config.get("SESSION_FACTORY")
    return session_factory() if session_factory else Session()


@auth_api_ns.route('/authorize')
class Authorize(Resource):
    @auth_api_ns.expect(authorize_model)
    def post(self):
        """
        POST /authorize

        Get an authorization code

        Requirements:
        - Required fields: username, password.
        - Field types: "username": str, "password": str, "quantity": int, "redirect_uri": str
        - username, password must be valid

        Response:
        - 200: Return an auth code
        - 400: Validation errors on required fields, fields types
        - 401: Unauthorized
        """
        # Validate required fields
        data = request.get_json(force=True)
        username = data.get('username')
        password = data.get('password')

        missing = []
        if not username:
            missing.append("username")
        if not password:
            missing.append("password")

        if missing:
            return {"error": "Missing required fields", "fields": missing}, 400

        redirect_uri = request.form.get('redirect_uri')

        # Validate field types
        errors = []
        validate_field_types(data, {"username": str, "password": str, "redirect_uri": str}, errors)
        if errors:
            return {"error": "; ".join(errors)}, 400

        with get_session() as session:
            user = session.query(User).filter_by(username=username).first()
            if not user or not user.verify_password(password):
                return {'error': 'Invalid username or password'}, 401

            # Simulate creating auth code
            code = secrets.token_urlsafe(16)
            auth_codes[code] = user.username

            # Redirect with code (normally you'd use HTTP redirect, here we simulate JSON)
            return {
                'redirect_uri': f'{redirect_uri}',
                'code': f'{code}'
            }, 200


@auth_api_ns.route('/token')
class Token(Resource):
    @auth_api_ns.expect(token_model)
    def post(self):
        """
        POST /token

        Get an access token

        Requirements:
        - Required fields: client_id, client_secret, code.
        - Field types: "client_id": str, "client_secret": str, "code": str, "redirect_uri": str
        - client_id, client_secret must be correct; code must be valid

        Response:
        - 200: Return an access token
        - 400: Validation errors on required fields, fields types
        - 401: Invalid client or code
        """
        data = request.get_json(force=True)
        client_id = data.get('client_id')
        client_secret = data.get('client_secret')
        code = data.get('code')
        redirect_uri = data.get('redirect_uri')
        # Validate required fields
        missing = []
        if not client_id:
            missing.append("client_id")
        if not client_secret:
            missing.append("client_secret")
        if not code:
            missing.append("code")

        if missing:
            return {"error": "Missing required fields", "fields": missing}, 400


        # Validate field types
        errors = []
        validate_field_types(data, {"client_id": str, "client_secret": str, "code": str, "redirect_uri": str}, errors)
        if errors:
            return {"error": "; ".join(errors)}, 400

        # Client verification
        if client_id != CLIENT_ID or client_secret != CLIENT_SECRET:
            return {'error': 'Invalid client'}, 401

        # Validate code
        if code not in auth_codes:
            return {'error': 'Invalid grant'}, 401

        username = auth_codes.pop(code)  # remove once used

        # if not redirect_uri.startswith("http://localhost"):
        #     return jsonify({'error': 'invalid_redirect_uri'}), 400

        # Get user role
        user = None
        with get_session() as session:
            user = session.query(User).filter_by(username=username).first()
            if not user:
                return {"error": "Forbidden: insufficient permission"}, 403

        # Issue access token
        payload = {
            "user_id": user.id,
            "role": user.role
        }
        access_token = generate_token(payload)

        return {
            'access_token': access_token,
            'token_type': 'bearer',
            'expires_in': TOKEN_EXPIRE_MINUTES,
            'redirect_uri': redirect_uri,
            'role': user.role
        }, 200

