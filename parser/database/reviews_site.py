from sqlalchemy import Column, Integer, String

from database import Base
from shemes.bank import BankiRuItem, SravniRuItem


class BankiRu(Base):
    bank_id = Column(String, primary_key=True, index=True)
    bank_name = Column(String)
    reviews_url = Column(String)

    @staticmethod
    def from_pydantic(bank: BankiRuItem):
        return BankiRu(
            bank_name=bank.bank_name,
            reviews_url=bank.reviews_url,
            bank_id=bank.id,
        )


class SravniBankInfo(Base):
    bank_id: str = Column(String, primary_key=True, index=True)
    sravni_id: str = Column(String)
    sravni_old_id: int = Column(Integer)
    alias: str = Column(String)
    bank_name: str = Column(String)
    bank_full_name: str = Column(String)
    bank_official_name: str = Column(String)

    @staticmethod
    def from_pydantic(bank: SravniRuItem):
        return SravniBankInfo(
            sravni_id=bank.sravni_id,
            sravni_old_id=bank.sravni_old_id,
            alias=bank.alias,
            bank_name=bank.bank_name,
            bank_full_name=bank.bank_full_name,
            bank_official_name=bank.bank_official_name,
            bank_id=bank.bank_id,
        )
