from typing import Optional, TYPE_CHECKING, List

from sqlmodel import VARCHAR, Column, Field, SQLModel, Relationship

if TYPE_CHECKING:
    from model.sravni_bank_info import SravniBankInfo
    from model.reviews import Reviews


class Banks(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    bank_name: str = Field(sa_column=Column("bank_name", VARCHAR, unique=True))
    bank_full_name: str
    bank_official_name: str
    description: Optional[str]
    sravni_info: "SravniBankInfo" = Relationship(back_populates="bank")
    reviews: List["Reviews"] = Relationship(back_populates="bank")
