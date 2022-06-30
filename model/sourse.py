from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

from sqlmodel import VARCHAR, Column, Field, SQLModel, Relationship

if TYPE_CHECKING:
    from model.reviews import Reviews


class Source(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    name: str = Field(sa_column=Column("site", VARCHAR, unique=True))
    last_checked: Optional[datetime]
    description: Optional[str]
    reviews: List["Reviews"] = Relationship(back_populates="source")
