from sqlalchemy import Column, Integer, String

from banki_ru_reviews.shemes import BankiRuItem
from utils.database import Base


class BankiRu(Base):
    __tablename__ = "banki_ru"

    id: int = Column(Integer, primary_key=True, index=True)
    bank_id: int = Column(Integer, index=True)  # some ids are not unique
    bank_name: str = Column(String)
    bank_code: str = Column(String)

    @staticmethod
    def from_pydantic(bank: BankiRuItem) -> "BankiRu":
        return BankiRu(
            bank_name=bank.bank_name,
            bank_code=bank.bank_code,
            bank_id=bank.bank_id,
        )
