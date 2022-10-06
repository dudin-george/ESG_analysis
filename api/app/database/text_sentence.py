from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.database.text import Text
    from app.database.text_result import TextResult


class TextSentence(Base):
    __tablename__ = "text_sentence"

    id = Column(Integer, primary_key=True)
    text_id = Column(Integer, ForeignKey("text.id"))
    text: Mapped["Text"] = relationship("Text", back_populates="text_sentences")
    sentence = Column(String)
    sentence_num = Column(Integer)
    text_results: Mapped[list["TextResult"]] = relationship("TextResult", back_populates="text_sentence")
    temp_sentences: "TempSentence" = relationship("TempSentence", back_populates="text_sentence")


class TempSentence(Base):
    __tablename__ = "temp_sentences"

    id = Column(Integer, primary_key=True)
    sentence_id = Column(Integer, ForeignKey("text_sentence.id"), index=True)
    sentence = Column(String, nullable=True)
    text_sentence: Mapped["TextSentence"] = relationship("TextSentence", back_populates="temp_sentences")
    query = Column(String, index=True)
