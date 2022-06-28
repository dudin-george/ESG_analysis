from typing import Optional

from sqlmodel import VARCHAR, Column, Field, SQLModel


class Banks(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    bank_name: str = Field(sa_column=Column("bank_name", VARCHAR, unique=True))
    bank_full_name: str
    bank_official_name: str
    description: Optional[str]
