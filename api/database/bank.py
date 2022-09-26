from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from database.base import Base


class Bank(Base):
    __tablename__ = "bank"

    id = Column(Integer, primary_key=True)
    bank_name = Column(String)
    bank_status = Column(String)
    description = Column(String)
    texts = relationship("Text", back_populates="bank")
