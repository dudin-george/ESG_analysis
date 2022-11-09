from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import Bank
from app.database.models.bank import BankType
from app.schemes.bank_types import BankTypeVal


async def create_bank_element_type(db: AsyncSession, bank_type_name: BankTypeVal) -> BankType:
    bank_type = await db.scalar(select(BankType).filter(BankType.name == bank_type_name))
    if bank_type:
        return bank_type
    bank_type = BankType(name=bank_type_name)
    db.add(bank_type)
    await db.commit()
    await db.refresh(bank_type)
    return bank_type


async def create_bank_type(db: AsyncSession) -> BankType:
    return await create_bank_element_type(db, BankTypeVal.bank)


async def get_bank_count(db: AsyncSession) -> int:
    return await db.scalar(select(func.count(Bank.id)))  # type: ignore


async def get_bank_list(db: AsyncSession) -> list[Bank]:
    return await db.scalars(select(Bank))  # type: ignore


async def load_banks(db: AsyncSession, banks: list[Bank]) -> None:
    db.add_all(banks)
    await db.commit()
