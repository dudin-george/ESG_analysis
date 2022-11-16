from pydantic import BaseModel


class Bank(BaseModel):
    id: int
    bank_name: str
    licence: str

    class Config:
        orm_mode = True


class GetBankList(BaseModel):
    items: list[Bank]
