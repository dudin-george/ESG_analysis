from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import Bank


async def get_bank_count(db: AsyncSession) -> int:
    return await db.scalar(select(func.count(Bank.id)))  # type: ignore


async def get_bank_list(db: AsyncSession) -> list[Bank]:
    return await db.scalars(select(Bank))  # type: ignore


async def load_bank(db: AsyncSession, banks: list[Bank]) -> None:
    db.add_all(banks)
    await db.commit()
