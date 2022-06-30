from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel

from model.models import Models
from model.text_model import TextModels


class TextResult(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    text: str
    sent_num: int
    model: List[Models] = Relationship(back_populates="text_results", link_model=TextModels)
    result: str  # TODO change type
