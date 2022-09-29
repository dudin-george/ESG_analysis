from sqlalchemy import Column, Integer, String

from database import Base
from shemes.bank import BankiRuItem, SravniRuItem


class BankiRu(Base):
    __tablename__ = "banki_ru"

    id: int = Column(Integer, primary_key=True, index=True)
    bank_id = Column(String, index=True)  # some ids are not unique
    bank_name = Column(String)
    reviews_url = Column(String)

    @staticmethod
    def from_pydantic(bank: BankiRuItem) -> "BankiRu":
        return BankiRu(
            bank_name=bank.bank_name,
            reviews_url=bank.reviews_url,
            bank_id=bank.bank_id,
        )


class SravniBankInfo(Base):
    __tablename__ = "sravni_bank_info"

    id: int = Column(Integer, primary_key=True, index=True)
    bank_id: str = Column(String, index=True)  # some ids are not unique (modulebank and hice)
    sravni_id: str = Column(String)
    sravni_old_id: int = Column(Integer)
    alias: str = Column(String)
    bank_name: str = Column(String)
    bank_full_name: str = Column(String)
    bank_official_name: str = Column(String)

    @staticmethod
    def from_pydantic(bank: SravniRuItem) -> "SravniBankInfo":
        return SravniBankInfo(
            sravni_id=bank.sravni_id,
            sravni_old_id=bank.sravni_old_id,
            alias=bank.alias,
            bank_name=bank.bank_name,
            bank_full_name=bank.bank_full_name,
            bank_official_name=bank.bank_official_name,
            bank_id=bank.bank_id,
        )
