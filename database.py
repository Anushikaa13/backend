from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./products.db"

engine = create_engine(
DATABASE_URL, connect_args={"check_same_thread": False}
)   #Day 8 - Safe concurrent access for SQLite
#Required for SQLite to allow multiple threads to access the database

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
