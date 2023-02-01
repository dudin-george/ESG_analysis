from typing import TYPE_CHECKING

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    extract,
    func,
)
from sqlalchemy.orm import Mapped, relationship

from app.database.models.base import Base

if TYPE_CHECKING:
    from app.database.models.bank import Bank
    from app.database.models.source import Source
    from app.database.models.text_sentence import TextSentence


class Text(Base):
    __tablename__ = "text"
    __table_args__ = (
        Index("ix_text_date_extract_year", extract("year", "date")),
        Index("ix_text_date_extract_quarter", extract("quarter", "date")),
        Index("ix_text_date_trunc_month", func.date_trunc("month", "date")),
    )

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

    def __repr__(self) -> str:
        return (
            f"Text(id={self.id}, link={self.link}, source_id={self.source_id}, date={self.date}, title={self.title},"
            f" bank_id={self.bank_id}, comment_num={self.comment_num})"
        )
