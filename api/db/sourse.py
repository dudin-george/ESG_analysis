from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import VARCHAR, Column, Field, Relationship, SQLModel

if TYPE_CHECKING:
    from db.reviews import Reviews


class Source(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    name: str = Field(sa_column=Column("site", VARCHAR, unique=True))
    last_checked: Optional[datetime]
    description: Optional[str]
    reviews: List["Reviews"] = Relationship(back_populates="source")
