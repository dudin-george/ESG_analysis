from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database.base import Base


class TextSentence(Base):
    __tablename__ = "text_sentence"

    id = Column(Integer, primary_key=True)
    text_id = Column(Integer, ForeignKey("text.id"))
    text = relationship("Text", back_populates="text_sentences")
    sentence = Column(String)
    sentence_num = Column(Integer)
    text_results = relationship("TextResult", back_populates="text_sentence")