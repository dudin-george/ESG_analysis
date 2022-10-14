from pydantic import BaseModel


class BankiRuItem(BaseModel):
    bank_id: int
    bank_name: str
    bank_code: str

    class Config:
        orm_mode = True
