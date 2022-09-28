from database import SessionLocal
from database.reviews_site import SravniBankInfo


def get_bank_list() -> list[SravniBankInfo]:
    with SessionLocal() as db:
        bank_list = db.query(SravniBankInfo).all()
    return bank_list


def create_banks(bank_list: list[SravniBankInfo]) -> None:
    with SessionLocal() as db:
        db.add_all(bank_list)
        db.commit()
