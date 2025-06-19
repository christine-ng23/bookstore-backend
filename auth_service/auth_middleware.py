### auth_service/auth_middleware.py
from functools import wraps
from flask import request, jsonify, g
import jwt

from .token_utils import verify_token


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authorization header missing or invalid'}), 401

        token = auth_header.split(' ')[1]
        try:
            payload = verify_token(token)
            # Attach to request contex
            g.user = {
                "user_id": payload["user_id"],
                "role": payload["role"]
            }
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except (jwt.InvalidTokenError, TypeError, KeyError):
            return jsonify({'error': 'Invalid token'}), 401
        return f(*args, **kwargs)
    return decorated

def require_role(role):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not hasattr(g, "user") or g.user.get("role") != role:
                return jsonify({"error": "Forbidden: insufficient permission"}), 403
            return f(*args, **kwargs)
        return wrapper
    return decorator
