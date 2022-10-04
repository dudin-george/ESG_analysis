from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.database.bank import Bank
    from app.database.source import Source
    from app.database.text_sentence import TextSentence


class Text(Base):
    __tablename__ = "text"

    id = Column(Integer, primary_key=True, index=True)
    link = Column(String)
    source_id = Column(Integer, ForeignKey("source.id"), index=True)
    source: Mapped["Source"] = relationship("Source", back_populates="texts")
    date = Column(DateTime, index=True)
    title = Column(String)
    bank_id = Column(Integer, ForeignKey("bank.id"), index=True)
    bank: Mapped["Bank"] = relationship("Bank", back_populates="texts")
    comment_num = Column(Integer, nullable=True)
    text_sentences: Mapped[list["TextSentence"]] = relationship("TextSentence", back_populates="text")
