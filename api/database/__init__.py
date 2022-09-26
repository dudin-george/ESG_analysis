from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.bank import Bank
from database.model import Model, ModelType
from database.source import Source
from database.text import Text
from database.text_result import TextResult
from database.text_sentence import TextSentence
from settings import Settings

engine = create_engine(Settings().database_url, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
