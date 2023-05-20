from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.query.bank import (
    get_bank_list,
    get_broker_list,
    get_insurance_list,
    get_mfo_list,
)
from app.schemes.bank import BankModel, GetBankList

router = APIRouter(prefix="/bank", tags=["bank"])


@router.get("/", response_model=GetBankList)
async def get_banks(db: AsyncSession = Depends(get_session)) -> GetBankList:
    banks_db = await get_bank_list(db)
    return GetBankList(items=[BankModel.from_orm(bank) for bank in banks_db])


@router.get("/broker", response_model=GetBankList)
async def get_broker(db: AsyncSession = Depends(get_session)) -> GetBankList:
    banks_db = await get_broker_list(db)
    return GetBankList(items=[BankModel.from_orm(bank) for bank in banks_db])


@router.get("/insurance", response_model=GetBankList)
async def get_insurance(db: AsyncSession = Depends(get_session)) -> GetBankList:
    banks_db = await get_insurance_list(db)
    return GetBankList(items=[BankModel.from_orm(bank) for bank in banks_db])


@router.get("/mfo", response_model=GetBankList)
async def get_mfo(db: AsyncSession = Depends(get_session)) -> GetBankList:
    banks_db = await get_mfo_list(db)
    return GetBankList(items=[BankModel.from_orm(bank) for bank in banks_db])
