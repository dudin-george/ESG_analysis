from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import Bank


def get_bank_count(db: Session):
    return db.query(func.count(Bank.id)).first()[0]


def load_bank(db: Session, banks: list[Bank]):
    db.add_all(banks)
    db.commit()
