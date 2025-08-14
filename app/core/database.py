from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.engine import URL
from app.core.config import settings

url = f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"

engine = create_engine(url)
SessionLocal = sessionmaker(autoflush=False, bind=engine, autocommit=False)

Base = declarative_base()


"""
What yield does:
Pauses execution at the yield statement and returns the database session (db) to the caller
Waits for the caller to finish using the database session
Resumes execution after yield when the caller is done, running the finally block to clean up
"""
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
