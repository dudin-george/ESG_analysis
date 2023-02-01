from sqlalchemy import Column, DateTime, Integer, String

from app.database.models.base import Base


class TextSentenceCount(Base):
    __tablename__ = "text_reviews_count"

    id = Column(Integer, primary_key=True)
    date = Column(DateTime, index=True)
    quarter = Column(Integer, index=True)
    source_site = Column(String, index=True)
    source_type = Column(String, index=True)
    count_reviews = Column(Integer)

    def __repr__(self) -> str:
        return (
            f"TextSentenceCount(date={self.date}, quarter={self.quarter}, source_site={self.source_site},"
            f" source_type={self.source_type}, count={self.count_reviews})"
        )
