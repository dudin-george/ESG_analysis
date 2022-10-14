from banki_ru.database import BankiRu
from common.database import SessionLocal


def get_bank_list() -> list[BankiRu]:
    with SessionLocal() as db:
        bank_list = db.query(BankiRu).order_by(BankiRu.bank_id).all()
    return bank_list


def create_banks(bank_list: list[BankiRu]) -> None:
    with SessionLocal() as db:
        db.add_all(bank_list)
        db.commit()
