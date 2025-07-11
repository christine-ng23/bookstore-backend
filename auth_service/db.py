## auth_service/db.py
from common.models import Base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from flask import current_app
from common.config import DB_PATH

def get_default_engine():
    return create_engine(f"sqlite:///{DB_PATH}", echo=True)

def get_default_session_factory():
    return sessionmaker(bind=get_default_engine())

def get_session():
    session_factory = current_app.config.get("SESSION_FACTORY")
    return session_factory() if session_factory else get_default_session_factory()()


def init_db(engine):
    # Init database once
    Base.metadata.create_all(engine)
    print("Database schema created")

if __name__ == '__main__':
    init_db(get_default_engine())

