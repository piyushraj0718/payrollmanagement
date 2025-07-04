from connection import engine
from db_setup import Base

def setup_database():
    """Create all tables in the database."""
    Base.metadata.create_all(engine)

if __name__ == "__main__":
    setup_database()
    print("Database tables created successfully.")
