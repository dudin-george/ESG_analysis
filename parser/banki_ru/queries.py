from banki_ru.database import (
    BankiRuBank,
    BankiRuBase,
    BankiRuBroker,
    BankiRuInsurance,
    BankiRuMfo,
)
from banki_ru.schemes import BankTypes
from common.database import get_sync


def get_bank_list(bank_site: BankTypes) -> list[BankiRuBase]:
    with get_sync() as db:
        match bank_site:
            case BankTypes.bank | BankTypes.news:
                bank_list = db.query(BankiRuBank).order_by(BankiRuBank.bank_id).all()
            case BankTypes.insurance:
                bank_list = db.query(BankiRuInsurance).order_by(BankiRuInsurance.bank_id).all()
            case BankTypes.mfo:
                bank_list = db.query(BankiRuMfo).order_by(BankiRuMfo.bank_id).all()
            case BankTypes.broker:
                bank_list = db.query(BankiRuBroker).order_by(BankiRuBroker.bank_id).all()
            case _:
                raise NotImplementedError
    return bank_list


def create_banks(bank_list: list[BankiRuBase]) -> None:
    with get_sync() as db:
        db.add_all(bank_list)
        db.commit()
