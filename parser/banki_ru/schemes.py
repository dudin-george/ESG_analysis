from enum import Enum

from pydantic import BaseModel


class BankiRuBankScheme(BaseModel):
    bank_id: int
    bank_name: str
    bank_code: str

    class Config:
        orm_mode = True


class MfoScheme(BaseModel):
    license: int
    name: str
    code: str
    ogrn: int

    def __hash__(self) -> int:
        return hash(self.license) + hash(self.ogrn) + hash(self.code) + hash(self.name)

    class Config:
        orm_mode = True


class BankTypes(str, Enum):
    bank = "banki.ru"
    news = "banki.ru/news"
    insurance = "banki.ru/insurance"
    mfo = "banki.ru/mfo"
    broker = "banki.ru/broker"
