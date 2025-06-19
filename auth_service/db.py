## auth_service/db.py
from sqlalchemy import create_engine

from common.constants import DB_PATH
from common.models import Base

engine = create_engine(f'sqlite:///{DB_PATH}')
Base.metadata.create_all(engine)
print("Auth DB initialized")
