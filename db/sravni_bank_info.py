from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from db.banks import Banks


class SravniBankInfo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    sravni_id: str = Field(default=None, max_length=30)
    sravni_old_id: int
    alias: str
    bank_name: str
    bank_full_name: str
    bank_official_name: str
    bank_id: str = Field(foreign_key="banks.id", default=None)
    bank: "Banks" = Relationship(back_populates="sravni_info")
