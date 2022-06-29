from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship

from model.Models import Models
from model.TextModel import TextModels


class TextResult(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    text: str
    sent_num: int
    model: List[Models] = Relationship(back_populates="text_results", link_model=TextModels)
    result: str  # TODO change type
