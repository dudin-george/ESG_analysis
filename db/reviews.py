from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import VARCHAR, Column, Field, Integer, Relationship, SQLModel

if TYPE_CHECKING:
    from db.banks import Banks
    from db.sourse import Source


class Reviews(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    link: str = Field(sa_column=Column("link", VARCHAR, unique=True))
    source_id: int = Field(default=None, foreign_key="source.id")
    source: "Source" = Relationship(back_populates="reviews")
    date: datetime
    title: str
    text: str
    bank_id: int = Field(default=None, foreign_key="banks.id")
    bank: "Banks" = Relationship(back_populates="reviews")
    rating: int = Field(sa_column=Column("rating", Integer, nullable=True))
    comments_num: int = Field(ge=0, default=0)
    user_id: Optional[str]
