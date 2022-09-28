from pydantic import BaseModel


class Bank(BaseModel):
    id: str
    bank_name: str

    class Config:
        orm_mode = True


class GetBankList(BaseModel):
    items: list[Bank]
