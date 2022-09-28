from database import get_db
from database.reviews_site import BankiRu


def get_bank_list() -> list[BankiRu]:
    with get_db() as db:
        bank_list = db.query(BankiRu).all()
    return bank_list


def create_banks(bank_list: list[BankiRu]):
    with get_db() as db:
        db.add_all(bank_list)
        db.commit()
