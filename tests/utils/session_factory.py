from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from common.config import DB_PATH, DB_NAME
from common.models import Base
from test_utils.data_loader import clean_data, initialize_data_from_json


def session_factory(session_type="in_memory", json_file=None):
    """
    Return a session factory based on type, and preload data. Types:
    - "in_memory"
    - "real"
    """
    if session_type == "in_memory":
        engine = create_engine("sqlite:///:memory:", echo=False)
        with engine.connect() as conn:
            conn.execute(text("PRAGMA foreign_keys=ON"))
        Base.metadata.create_all(engine)
        print(f"Database schema created in :memory")

    elif session_type == "real":
        engine = create_engine(f"sqlite:///{DB_PATH}")
        with engine.connect() as conn:
            conn.execute(text("PRAGMA foreign_keys=ON"))
        Base.metadata.create_all(engine)
        print(f"Database schema created in {DB_NAME}")

    else:
        raise ValueError(f"Unsupported session type: {type}")

    Session = sessionmaker(bind=engine)
    session = Session()
    # Clean data
    clean_data(session)
    # Preload data if specified
    if json_file:
        initialize_data_from_json(session, json_file)
    session.close()

    return Session
