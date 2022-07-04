from typing import TYPE_CHECKING, List, Optional

from sqlmodel import VARCHAR, Column, Field, Relationship, SQLModel

if TYPE_CHECKING:
    from db.reviews import Reviews
    from db.sites_banks import InfoBankiRu, SravniBankInfo


class Banks(SQLModel, table=True):
    id: str = Field(primary_key=True, index=True)
    bank_name: str = Field(sa_column=Column("bank_name", VARCHAR, unique=True))
    bank_status: Optional[str]
    description: Optional[str]
    sravni_info: "SravniBankInfo" = Relationship(back_populates="bank")
    bankiru_bank: "InfoBankiRu" = Relationship(back_populates="bank")
    reviews: List["Reviews"] = Relationship(back_populates="bank")
