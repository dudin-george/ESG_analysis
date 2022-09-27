from pydantic import BaseModel


class Bank(BaseModel):
    id: str
    bank_name: str
