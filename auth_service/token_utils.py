## auth_service/token_utils.py
import jwt
from datetime import datetime, timezone, timedelta

from auth_service.config import SECRET, TOKEN_EXPIRE_MINUTES


def generate_token(payload):
    payload['exp'] = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    return jwt.encode(payload, SECRET, algorithm='HS256')

def verify_token(token):
    return jwt.decode(token, SECRET, algorithms=['HS256'])

