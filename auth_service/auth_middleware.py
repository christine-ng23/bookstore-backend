### auth_service/auth_middleware.py
from functools import wraps

import jwt
from flask import request, jsonify, g

from .token_utils import verify_token


def require_auth(optional=False):
    def inner_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                if optional:
                    g.user = None
                    return f(*args, **kwargs)
                else:
                    return jsonify({'error': 'Authorization header missing or invalid'}), 401

            token = auth_header.split(' ')[1]
            try:
                payload = verify_token(token)
            except jwt.ExpiredSignatureError:
                if optional:
                    g.user = None
                    return f(*args, **kwargs)
                return jsonify({'error': 'Token expired'}), 401
            except jwt.InvalidTokenError:
                if optional:
                    g.user = None
                    return f(*args, **kwargs)
                return jsonify({'error': 'Invalid token'}), 401

            try: # Attach to request context
                g.user = {
                    "user_id": payload["user_id"],
                    "role": payload["role"]
                }
            except (TypeError, KeyError) as ex:
                if optional:
                    g.user = None
                    return f(*args, **kwargs)
                # return jsonify({'error': 'Invalid token'}), 401
                return jsonify({'error': f'Invalid token payload: missing {ex}'}), 401

            return f(*args, **kwargs)

        return wrapper

    return inner_decorator


def require_role(role):
    def inner_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not hasattr(g, "user") or g.user.get("role") != role:
                return jsonify({"error": "Forbidden: insufficient permission"}), 403
            return f(*args, **kwargs)

        return wrapper

    return inner_decorator
