from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, relationship

from app.database.models.base import Base

if TYPE_CHECKING:
    from app.database.models.text import Text


class SourceType(Base):
    __tablename__ = "source_type"

    id = Column(Integer, primary_key=True)
    name = Column(String, index=True, unique=True)
    sources: Mapped[list["Source"]] = relationship("Source", back_populates="source_type")

    def __repr__(self) -> str:
        return f"SourceType(id={self.id}, name={self.name})"


class Source(Base):
    __tablename__ = "source"

    id = Column(Integer, primary_key=True)
    site = Column(String, index=True, unique=True)
    source_type_id = Column(Integer, ForeignKey("source_type.id"), index=True)
    source_type: Mapped["SourceType"] = relationship("SourceType", back_populates="sources")
    parser_state = Column(String, nullable=True)
    last_update = Column(DateTime, nullable=True)
    texts: Mapped[list["Text"]] = relationship("Text", back_populates="source")

    def __repr__(self) -> str:
        return (
            f"Source(id={self.id}, site={self.site}, source_type_id={self.source_type_id},"
            f" parser_state={self.parser_state}, last_update={self.last_update})"
        )
