from typing import TYPE_CHECKING

from sqlalchemy import ARRAY, Column, Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.database.model import Model
    from app.database.text_sentence import TextSentence


class TextResult(Base):
    __tablename__ = "text_result"

    id = Column(Integer, primary_key=True, index=True)
    text_sentence_id = Column(Integer, ForeignKey("text_sentence.id"), index=True)
    text_sentence: Mapped["TextSentence"] = relationship("TextSentence", back_populates="text_results")
    model_id = Column(Integer, ForeignKey("model.id"), index=True)
    model: Mapped["Model"] = relationship("Model", back_populates="text_results")
    result: list[float] = Column(ARRAY(Float))  # type: ignore
