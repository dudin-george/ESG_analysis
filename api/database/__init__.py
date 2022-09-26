import os

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from database.bank import Bank
from database.model import ModelType, Model
from database.text import Text
from database.text_sentence import TextSentence
from database.text_result import TextResult
from database.source import Source


DATABASE_URL = os.environ.get("DATABASE_URL", None)
if DATABASE_URL is None:
    raise ValueError("DATABASE_URL is not set")
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
