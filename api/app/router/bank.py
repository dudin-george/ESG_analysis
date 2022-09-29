from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.query.bank import get_bank_list
from app.schemes.bank import Bank, GetBankList

router = APIRouter(prefix="/bank", tags=["bank"])


@router.get("/", response_model=GetBankList)
async def get_banks(db: Session = Depends(get_db)) -> GetBankList:
    banks_db = await get_bank_list(db)
    get_bank_list_return = GetBankList(items=[])
    for bank in banks_db:
        bank_return = Bank.from_orm(bank)
        get_bank_list_return.items.append(bank_return)
    return get_bank_list_return
