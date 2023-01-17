from datetime import date
from enum import Enum

from pydantic import BaseModel


class IndexTypeVal(str, Enum):
    default_index = "index"
    index_std = "index_std"


class AggregateTextResultItem(BaseModel):
    year: int
    quarter: int
    date: date
    bank_name: str
    bank_id: int
    model_name: str
    source_type: str
    index: float

    def __repr__(self) -> str:
        return (
            f"AggregateTextResultItem(year={self.year}, quarter={self.quarter}, bank_name={self.bank_name},"
            f" model_name={self.model_name}, source_type={self.source_type}, index={self.index})"
        )


class AggregateTetResultResponse(BaseModel):
    items: list[AggregateTextResultItem]
