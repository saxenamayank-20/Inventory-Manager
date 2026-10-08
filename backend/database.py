from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

# load .env
load_dotenv()

# no DATABASE_URL (or an empty one) means local sqlite
DATABASE_URL = os.getenv("DATABASE_URL") or "sqlite:///./inventory.db"

engine = create_engine(
    DATABASE_URL,
    echo=True,  # prints every sql query
    pool_pre_ping=True  # reconnect if mysql dropped the connection
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# base class for the models
Base = declarative_base()


def get_db():
    # one session per request, closed when the request is done
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
