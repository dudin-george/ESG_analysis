from typing import Optional, TYPE_CHECKING

from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from model.banks import Banks


class SravniBankInfo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    sravni_id: str = Field(default=None, max_length=30)
    sravni_old_id: int
    alias: str
    bank_id: int = Field(foreign_key="banks.id")
    bank: "Banks" = Relationship(back_populates="sravni_info")
