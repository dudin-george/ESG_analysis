from datetime import date
from enum import Enum

from pydantic import BaseModel


class IndexTypeVal(str, Enum):
    index_base = "index_base"
    index_mean = "index_mean"
    index_std = "index_std"
    index_safe = "index_safe"


class AggregateTextResultItem(BaseModel):
    year: int
    quarter: int
    date: date
    bank_name: str
    bank_id: int
    model_name: str
    source_type: str
    index: float | None

    def __repr__(self) -> str:
        return (
            f"AggregateTextResultItem(year={self.year}, quarter={self.quarter}, bank_name={self.bank_name},"
            f" model_name={self.model_name}, source_type={self.source_type}, index={self.index})"
        )


class AggregateTetResultResponse(BaseModel):
    items: list[AggregateTextResultItem]
