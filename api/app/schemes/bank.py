from pydantic import BaseModel


class Bank(BaseModel):
    id: int
    bank_name: str
    licence: str
    description: str | None = None

    class Config:
        orm_mode = True


class GetBankList(BaseModel):
    items: list[Bank]
