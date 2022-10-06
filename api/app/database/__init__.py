from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.database.bank import Bank  # noqa: F401
from app.database.model import Model, ModelType  # noqa: F401
from app.database.source import Source, SourceType  # noqa: F401
from app.database.text import Text  # noqa: F401
from app.database.text_result import TextResult  # noqa: F401
from app.database.text_sentence import TextSentence, TempSentence  # noqa: F401
from app.settings import Settings

engine = create_engine(Settings().database_url, echo=Settings().echo)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Iterator[Session]:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
