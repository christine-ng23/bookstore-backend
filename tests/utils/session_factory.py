from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from common.constants import DB_PATH
from common.models import Base
from tests.utils.data_loader import initialized_data, clean_data


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

    elif session_type == "real":
        engine = create_engine(f"sqlite:///{DB_PATH}")
        with engine.connect() as conn:
            conn.execute(text("PRAGMA foreign_keys=ON"))
        Base.metadata.create_all(engine)

    else:
        raise ValueError(f"Unsupported session type: {type}")

    Session = sessionmaker(bind=engine)
    session = Session()
    # Clean data
    clean_data(session)
    # Preload data if specified
    if json_file:
        initialized_data(session, json_file)
    session.close()

    return Session
