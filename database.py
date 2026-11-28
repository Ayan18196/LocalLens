import os
from dotenv import load_dotenv
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, hide_parameters=True) if DATABASE_URL else None

SessionLocal = sessionmaker(bind=engine, autoflush=False)

Base = declarative_base()


# Opens and closes the database session
def get_db():
    if engine is None:
        raise HTTPException(
            status_code=503,
            detail={
                "code": "DATABASE_UNAVAILABLE",
                "message": "The database is not configured.",
            },
        )
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()