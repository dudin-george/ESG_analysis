from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from database.base import Base


class SourceType(Base):
    __tablename__ = "source_type"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    sources = relationship("Source", back_populates="source_type")


class Source(Base):
    __tablename__ = "source"

    id = Column(Integer, primary_key=True)
    site = Column(String)
    source_type_id = Column(Integer, ForeignKey("source_type.id"))
    source_type = relationship("SourceType", back_populates="sources")
    parser_state = Column(String, nullable=True)
    last_update = Column(DateTime, nullable=True)
