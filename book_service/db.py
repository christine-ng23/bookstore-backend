## book_service/db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from common.constants import DB_PATH
from .models import Base

engine = create_engine(f'sqlite:///{DB_PATH}', echo=True)
Session = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine)
    print("Database schema created")

if __name__ == '__main__':
    init_db()
