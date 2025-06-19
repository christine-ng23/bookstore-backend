## auth_service/init_admin.py
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from common.constants import DB_PATH
from common.models import User

engine = create_engine(f'sqlite:///{DB_PATH}')
Session = sessionmaker(bind=engine)
session = Session()
try:
    res = session.query(User).filter_by(username='admin').first()
    if not res:
        admin = User(username='admin', role='admin')
        admin.set_password('admin')
        session.add(admin)
        session.commit()
        print("Default admin user created")
    else:
        print(f"Admin user already exists: (id:{res.id}, username: {res.username}, role: {res.role})")
except Exception as e:
    print(e)

