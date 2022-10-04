from database import SessionLocal
from sravni_reviews.database import SravniBankInfo


def get_bank_list() -> list[SravniBankInfo]:
    with SessionLocal() as db:
        bank_list = db.query(SravniBankInfo).order_by(SravniBankInfo.bank_id).all()
    return bank_list


def create_banks(bank_list: list[SravniBankInfo]) -> None:
    with SessionLocal() as db:
        db.add_all(bank_list)
        db.commit()
