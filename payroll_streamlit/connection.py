import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging

logging.basicConfig(level=logging.WARNING)
logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "plus2_payroll.db")

# Added connect_args to allow multi-threading with Streamlit
engine = create_engine(f"sqlite:///{DB_NAME}", connect_args={"check_same_thread": False})

Session = sessionmaker(bind=engine)

def get_session():
    return Session()


