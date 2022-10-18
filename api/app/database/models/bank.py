from typing import TYPE_CHECKING

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Mapped, relationship

from app.database.models.base import Base

if TYPE_CHECKING:
    from app.database.models.text import Text


class Bank(Base):
    __tablename__ = "bank"

    id = Column(Integer, primary_key=True, index=True)
    bank_name = Column(String)
    description = Column(String, nullable=True)
    texts: Mapped[list["Text"]] = relationship("Text", back_populates="bank")

    def __repr__(self) -> str:
        return f"Bank(id={self.id}, bank_name={self.bank_name}, description={self.description})"
