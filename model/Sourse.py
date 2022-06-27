from datetime import datetime
from typing import Optional

from sqlmodel import VARCHAR, Column, Field, SQLModel


class Source(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    site: str = Field(sa_column=Column("site", VARCHAR, unique=True))
    last_checked: Optional[datetime]
