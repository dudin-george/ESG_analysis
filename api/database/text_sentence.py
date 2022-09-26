from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, relationship

from database.base import Base

if TYPE_CHECKING:
    from database.text import Text
    from database.text_result import TextResult


class TextSentence(Base):
    __tablename__ = "text_sentence"

    id = Column(Integer, primary_key=True)
    text_id = Column(Integer, ForeignKey("text.id"))
    text: Mapped["Text"] = relationship("Text", back_populates="text_sentences")
    sentence = Column(String)
    sentence_num = Column(Integer)
    text_results: Mapped[list["TextResult"]] = relationship("TextResult", back_populates="text_sentence")
