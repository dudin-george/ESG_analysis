from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from utils.settings import Settings

Base = declarative_base()
engine = create_engine(Settings().database_url, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Iterator[Session]:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
