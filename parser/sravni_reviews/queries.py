from common.database import get_sync
from sravni_reviews.database import SravniBankInfo


def get_bank_list() -> list[SravniBankInfo]:
    with get_sync() as db:
        bank_list = db.query(SravniBankInfo).order_by(SravniBankInfo.bank_id).all()
    return bank_list


def create_banks(bank_list: list[SravniBankInfo]) -> None:
    with get_sync() as db:
        db.add_all(bank_list)
        db.commit()
