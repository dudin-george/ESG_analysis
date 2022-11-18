from common.database import SessionLocal
from vk_parser.database import VkBank, VkOtherIndustries, VKBaseDB
from vk_parser.schemes import VKType


def get_bank_list(bank_type: VKType) -> list[VKBaseDB]:
    with SessionLocal() as db:
        match bank_type:
            case VKType.bank:
                bank_list = db.query(VkBank).order_by(VkBank.id).all()
            case VKType.other:
                bank_list = db.query(VkOtherIndustries).order_by(VkOtherIndustries.id).all()
    return bank_list


def create_banks(bank_list: list[VKBaseDB]) -> None:
    with SessionLocal() as db:
        db.add_all(bank_list)
        db.commit()
