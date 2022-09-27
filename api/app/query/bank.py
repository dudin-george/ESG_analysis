from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import Bank


def get_bank_count(db: Session) -> int:
    return db.query(func.count(Bank.id)).first()[0]  # type: ignore


def load_bank(db: Session, banks: list[Bank]) -> None:
    db.add_all(banks)
    db.commit()
