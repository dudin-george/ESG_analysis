from typing import TYPE_CHECKING, List, Optional

from sqlmodel import VARCHAR, Column, Field, Relationship, SQLModel

if TYPE_CHECKING:
    from db.banki_ru_info import BankiRuBank
    from db.reviews import Reviews
    from db.sravni_bank_info import SravniBankInfo


class Banks(SQLModel, table=True):
    id: str = Field(primary_key=True, index=True)
    bank_name: str = Field(sa_column=Column("bank_name", VARCHAR, unique=True))
    bank_status: Optional[str]
    description: Optional[str]
    sravni_info: "SravniBankInfo" = Relationship(back_populates="bank")
    banki_ru_info: "BankiRuBank" = Relationship(back_populates="bank_cbr")
    reviews: List["Reviews"] = Relationship(back_populates="bank")
