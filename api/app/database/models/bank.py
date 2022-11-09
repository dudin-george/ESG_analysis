from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, relationship

from app.database.models.base import Base

if TYPE_CHECKING:
    from app.database.models.text import Text


class BankType(Base):
    __tablename__ = "bank_type"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    banks: Mapped["Bank"] = relationship("Bank", back_populates="bank_type")

    def __repr__(self) -> str:
        return f"BankType(id={self.id}, name={self.name})"


class Bank(Base):
    __tablename__ = "bank"

    id = Column(Integer, primary_key=True, index=True)
    bank_type_id = Column(Integer, ForeignKey("bank_type.id"), index=True, nullable=True)
    bank_type: Mapped["BankType"] = relationship("BankType", back_populates="banks")
    bank_name = Column(String)
    description = Column(String, nullable=True)
    texts: Mapped[list["Text"]] = relationship("Text", back_populates="bank")

    def __repr__(self) -> str:
        return f"Bank(id={self.id}, bank_name={self.bank_name}, description={self.description})"
