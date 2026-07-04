from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL is not set. Check your .env file."
    )

_kwargs = {"pool_pre_ping": True}

if DATABASE_URL.startswith("postgresql"):
    _kwargs["connect_args"] = {"connect_timeout": 5}
elif "sqlite" in DATABASE_URL:
    _kwargs["connect_args"] = {"check_same_thread": False}
    _kwargs["poolclass"] = StaticPool

engine = create_engine(DATABASE_URL, **_kwargs)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)
