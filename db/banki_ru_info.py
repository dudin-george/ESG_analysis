from typing import TYPE_CHECKING

from sqlmodel import VARCHAR, Column, Field, Relationship, SQLModel

if TYPE_CHECKING:
    from db.banks import Banks


class BankiRuBank(SQLModel, table=True):
    id: str = Field(default=None, primary_key=True, index=True)
    bank_name: str = Field(sa_column=Column("bank_name", VARCHAR, unique=True))
    reviews_url: str
    bank_id: str = Field(foreign_key="banks.id", default=None)  # TODO remove default(?)
    bank_cbr: "Banks" = Relationship(back_populates="banki_ru_info")
