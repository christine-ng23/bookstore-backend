## utils/handlers.py
from functools import wraps
from flask import jsonify
from sqlalchemy.exc import IntegrityError, InvalidRequestError

def handle_exceptions(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as ve:
            return jsonify({"error": str(ve)}), 400
        except IntegrityError:
            return jsonify({"error": "Database integrity error (e.g. duplicate or null constraint)"}), 409
        except InvalidRequestError:
            return jsonify({"error": "Invalid request or relationship management issue"}), 400
        except KeyError as ke:
            return jsonify({"error": f"Missing field: {str(ke)}"}), 400
        except TypeError as te:
            return jsonify({"error": f"Type error: {str(te)}"}), 400
        except Exception as e:
            return jsonify({"error": f"Unexpected server error: {str(e)}"}), 500
    return decorated_function

