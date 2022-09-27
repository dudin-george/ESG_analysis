from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.bank import Bank
from app.database.model import Model, ModelType
from app.database.source import Source
from app.database.text import Text
from app.database.text_result import TextResult
from app.database.text_sentence import TextSentence
from app.settings import Settings

engine = create_engine(Settings().database_url, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
