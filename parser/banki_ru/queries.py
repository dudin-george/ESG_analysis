from banki_ru.database import BankiRuBank
from common.database import SessionLocal


def get_bank_list() -> list[BankiRuBank]:
    with SessionLocal() as db:
        bank_list = db.query(BankiRuBank).order_by(BankiRuBank.bank_id).all()
    return bank_list


def create_banks(bank_list: list[BankiRuBank]) -> None:
    with SessionLocal() as db:
        db.add_all(bank_list)
        db.commit()
