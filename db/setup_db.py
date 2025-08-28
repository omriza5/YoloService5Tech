import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


DB_BACKEND = os.getenv("DB_BACKEND", "sqlite")
Base = declarative_base()

DATABASE_URL = os.getenv("DATABASE_URL")

if DB_BACKEND == "postgres":
    print("Using PostgreSQL as the database backend.")
    DATABASE_URL = "postgresql://user:pass@postgres/predictions"

else:
    print("Using SQLite as the database backend.")
    DATABASE_URL = "sqlite:///./predictions.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

