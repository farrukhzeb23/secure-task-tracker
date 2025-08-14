from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.engine import URL
from app.core.config import settings

url = URL.create(
    drivername="postgresql",
    username=settings.DB_USER,
    password=settings.DB_PASSWORD,
    host=settings.DB_HOST,
    port=int(settings.DB_PORT)
)

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
