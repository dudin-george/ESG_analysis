from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database.base import Base


class Text(Base):
    __tablename__ = "text"

    id = Column(Integer, primary_key=True)
    link = Column(String)
    source_id = Column(Integer, ForeignKey("source.id"))
    source = relationship("Source", back_populates="texts")
    date = Column(DateTime)
    title = Column(String)
    bank_id = Column(Integer, ForeignKey("bank.id"))
    bank = relationship("Bank", back_populates="texts")
    comment_num = Column(Integer, nullable=True)
    text_sentences = relationship("TextSentence", back_populates="text")
