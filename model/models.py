from typing import Optional, List, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship

from model.text_model import TextModels

if TYPE_CHECKING:
    from model.text_results import TextResult


class Models(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    model_path: str
    text_results: List["TextResult"] = Relationship(back_populates="model", link_model=TextModels)
