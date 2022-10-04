from database import SessionLocal
from database.reviews_site import BankiRu


def get_bank_list() -> list[BankiRu]:
    with SessionLocal() as db:
        bank_list = db.query(BankiRu).order_by(BankiRu.id).all()
    return bank_list


def create_banks(bank_list: list[BankiRu]) -> None:
    with SessionLocal() as db:
        db.add_all(bank_list)
        db.commit()
