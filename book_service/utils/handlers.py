## utils/handlers.py
import inspect
from functools import wraps
from flask import jsonify, request
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from werkzeug.exceptions import BadRequest

from common.exceptions import ForbiddenError, RecordNotFoundError


def handle_exceptions(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as ve:
            return jsonify({"error": str(ve)}), 400
        except ForbiddenError as e:
            return jsonify({"error": str(e)}), 403
        except IntegrityError as ie:
            return jsonify({"error": f"Database integrity error (e.g. duplicate or null constraint): {ie}"}), 409
            # Resource conflict
        except InvalidRequestError as ir:
            return jsonify({"error": f"{ir}"}), 400
        except RecordNotFoundError as rnf:
            return jsonify({"error": f'{rnf}'}), 404
        except BadRequest as e:
            # Often triggered by malformed JSON
            return jsonify({"error": str(e.description)}), 400
        except KeyError as ke:
            return jsonify({"error": f"Missing field: {str(ke)}"}), 400
        except TypeError as te:
            return jsonify({"error": f"Type error: {str(te)}"}), 400
        except Exception as e:
            if ((hasattr(e, "description") and "Failed to decode JSON" in str(e.description))
                    or request.content_type != "application/json"):
                return jsonify({"error": "Invalid or missing JSON in request body"}), 415
            return jsonify({"error": f"Unexpected server error: {str(e)}"}), 500
    return decorated_function


def validate_types(**type_hints):
    """
    Decorator to validate argument types at runtime.

    Usage:
    @validate_types(username=str, age=int)
    def register_user(username, age): ...
    """
    def inner_decorator(fn):
        sig = inspect.signature(fn)

        @wraps(fn)
        def wrapper(*args, **kwargs):
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            for name, expected_type in type_hints.items():
                if name in bound_args.arguments:
                    value = bound_args.arguments[name]
                    if isinstance(expected_type, type):
                        if not isinstance(value, expected_type):
                            raise TypeError(
                                f"Argument '{name}' must be of type {expected_type.__name__}, "
                                f"got {type(value).__name__}"
                            )
                    else:
                        if not any(isinstance(value, t) for t in expected_type):
                            raise TypeError(
                                f"Argument '{name}' must be of types ({', '.join([t.__name__ for t in expected_type])}')"
                                f"got {type(value).__name__}"
                            )

            return fn(*args, **kwargs)
        return wrapper
    return inner_decorator
