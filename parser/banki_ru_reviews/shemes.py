from pydantic import BaseModel


class BankiRuItem(BaseModel):
    bank_id: int
    bank_name: str
    reviews_url: str

    class Config:
        orm_mode = True
