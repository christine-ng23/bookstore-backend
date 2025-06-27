## book_service/db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from common.constants import DB_PATH
from .models import Base

# engine = create_engine(f'sqlite:///{DB_PATH}', echo=True)
# Session = sessionmaker(bind=engine)

def get_default_session_factory():
    return sessionmaker(bind=get_default_engine())

def get_default_engine():
    return create_engine(f"sqlite:///{DB_PATH}", echo=True)

def init_db(engine):
    # Init database once
    Base.metadata.create_all(engine)
    print("Database schema created")

if __name__ == '__main__':
    init_db(get_default_engine())
