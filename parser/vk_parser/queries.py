from utils.database import SessionLocal
from vk_parser.database import VkBank


def get_bank_list() -> list[VkBank]:
    with SessionLocal() as db:
        bank_list = db.query(VkBank).order_by(VkBank.id).all()
    return bank_list


def create_banks(bank_list: list[VkBank]) -> None:
    with SessionLocal() as db:
        db.add_all(bank_list)
        db.commit()
