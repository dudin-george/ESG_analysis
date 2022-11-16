from sqlalchemy import Column, Integer, String, BigInteger

from banki_ru import schemes
from common.database import Base


class BankiRuBank(Base):
    __tablename__ = "banki_ru"

    id: int = Column(Integer, primary_key=True, index=True)
    bank_id: int = Column(Integer, index=True)  # some ids are not unique
    bank_name: str = Column(String)
    bank_code: str = Column(String)

    @staticmethod
    def from_pydantic(bank: schemes.BankiRuBankScheme) -> "BankiRuBank":
        return BankiRuBank(
            bank_name=bank.bank_name,
            bank_code=bank.bank_code,
            bank_id=bank.bank_id,
        )


class BankiRuInsurance(BankiRuBank):
    __tablename__ = "banki_ru_insurance"


class BankiRuMfo(BankiRuBank):
    __tablename__ = "banki_ru_mfo"

    bank_id = Column(BigInteger, index=True)


class BankiRuBroker(BankiRuBank):
    __tablename__ = "banki_ru_broker"

    bank_id = Column(BigInteger, index=True)
