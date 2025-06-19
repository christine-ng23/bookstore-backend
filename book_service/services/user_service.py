### book_service/services/user_service.py
from passlib.hash import bcrypt
from sqlalchemy.orm import Session
from common.models import User

def list_users(session: Session):
    return session.query(User).all()

def register_user(session: Session, data: dict):
    user = User(**data)
    user.role = 'user'
    user.password = bcrypt.hash(user.password)
    session.add(user)
    session.commit()
    return user
# eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJyb2xlIjoiYWRtaW4iLCJleHAiOjE3NTAyNjQ4ODR9.5bJCryWJCpBJIjtlnewBxV3ZJcBzYyF704JNXWl2D4Q
# eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoyLCJyb2xlIjoidXNlciIsImV4cCI6MTc1MDI2NDk0NH0.UPhbuPniZkCbOfcCqp9HUgFRCnih8ibyN9C9EYUybsM
def get_user_by_username(session: Session, username: str):
    return session.query(User).filter(User.username == username).first()

def update_user(session: Session, user_id: int, updates: dict):
    user = session.query(User).filter(User.id == user_id).first()
    if user:
        for k, v in updates.items():
            setattr(user, k, v)
        if 'password' in updates:
            user.password = bcrypt.hash(user.password)
        session.commit()
    return user

def delete_user(session: Session, user_id: int):
    user = session.query(User).filter(User.id == user_id).first()
    if user:
        session.delete(user)
        session.commit()
    return user
