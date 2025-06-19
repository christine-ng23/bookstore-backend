## common/models.py
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String
from passlib.hash import bcrypt

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, default='user')

    def verify_password(self, raw_password):
        return bcrypt.verify(raw_password, self.password)

    def set_password(self, raw_password):
        self.password = bcrypt.hash(raw_password)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role
        }
