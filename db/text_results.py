from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

from db.text_model import TextModels

if TYPE_CHECKING:
    from db.models import Models
    from db.reviews import Reviews


class TextResult(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    review_id: int = Field(default=None, foreign_key="reviews.id")
    review: "Reviews" = Relationship(back_populates="text_results")
    sent_num: int
    sentence: str
    model: List["Models"] = Relationship(back_populates="text_results", link_model=TextModels)
    result: str  # TODO change type
