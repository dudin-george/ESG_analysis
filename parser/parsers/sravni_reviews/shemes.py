from pydantic import BaseModel


class SravniRuItem(BaseModel):
    sravni_id: str
    sravni_old_id: int
    alias: str
    bank_name: str
    bank_full_name: str
    bank_official_name: str
    bank_id: int

    class Config:
        orm_mode = True
