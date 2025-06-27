## auth_service/token_utils.py
import jwt
from datetime import datetime, timezone, timedelta

from jwt import ExpiredSignatureError, InvalidTokenError, DecodeError

from auth_service.config import SECRET, TOKEN_EXPIRE_MINUTES
from book_service.utils.handlers import validate_types


@validate_types(payload=dict)
def generate_token(payload: dict):
    payload['exp'] = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    return jwt.encode(payload, SECRET, algorithm='HS256')

@validate_types(token=str)
def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET, algorithms=['HS256'])
    except ExpiredSignatureError as e:
        raise e
    except (InvalidTokenError, DecodeError):
        raise InvalidTokenError("Invalid token")
    return payload
