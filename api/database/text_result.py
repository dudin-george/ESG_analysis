from sqlalchemy import ARRAY, Column, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship

from database.base import Base


class TextResult(Base):
    __tablename__ = "text_result"

    id = Column(Integer, primary_key=True)
    text_sentence_id = Column(Integer, ForeignKey("text_sentence.id"))
    text_sentence = relationship("TextSentence", back_populates="text_results")
    model_id = Column(Integer, ForeignKey("model.id"))
    model = relationship("Model", back_populates="text_results")
    result = Column(ARRAY(Float))
