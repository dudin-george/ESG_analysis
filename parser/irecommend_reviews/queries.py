from common.database import SessionLocal
from irecommend_reviews.database import IRecommend


def get_bank_list() -> list[IRecommend]:
    with SessionLocal() as db:
        bank_list = db.query(IRecommend).order_by(IRecommend.bank_id).all()
    return bank_list


def create_banks(bank_list: list[IRecommend]) -> None:
    with SessionLocal() as db:
        db.add_all(bank_list)
        db.commit()
