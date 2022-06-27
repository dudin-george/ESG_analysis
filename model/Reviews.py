from datetime import datetime
from typing import Optional

from sqlmodel import VARCHAR, Column, Field, Integer, SQLModel


class Reviews(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    link: str = Field(sa_column=Column("link", VARCHAR, unique=True))
    source: int = Field(default=None, foreign_key="source.id")
    date: datetime
    title: str
    text: str
    rating: int = Field(sa_column=Column("rating", Integer, nullable=True))
    comments_num: int = Field(ge=0, default=0)
    user_id: Optional[str]
