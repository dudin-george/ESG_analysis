from typing import Optional

from sqlmodel import Field, SQLModel


class SravniBankInfo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    bank_id: int = Field(foreign_key="banks.id")
    sravni_id: str = Field(default=None, primary_key=True, max_length=30, index=True)
    sravni_old_id: int
    alias: str
