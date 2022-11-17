import re
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, validator


class ApiBank(BaseModel):
    id: int
    bank_name: str
    licence: int


class Bank(BaseModel):
    id: int
    bank_name: str
    licence: int


class Source(BaseModel):
    id: int | None = None
    site: str
    source_type_id: int
    parser_state: str | None = None
    last_update: datetime | None = None


class Text(BaseModel):
    source_id: int
    date: datetime
    title: str
    text: str
    bank_id: int
    link: str
    comments_num: int | None = None

    @validator("text")
    def text_validator(cls, v: str) -> str:
        s = re.sub("[\xa0\n\t]", " ", v)
        return re.sub("<[^>]*>", "", s).strip()

    @validator("date", pre=True)
    def date_validator(cls, v: str | datetime) -> datetime:
        if type(v) is datetime:
            return v
        if type(v) is str and len(v.split(":")) == 3:
            return datetime.strptime(v, "%Y-%m-%d %H:%M:%S")
        if type(v) is str:
            return datetime.strptime(v, "%d.%m.%Y %H:%M")
        return v  # type: ignore

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class TextRequest(BaseModel):
    items: list[Text]
    parsed_state: str | None = None
    last_update: datetime | None = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class PatchSource(BaseModel):
    parser_state: str | None = None
    last_update: datetime | None = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class SourceRequest(BaseModel):
    site: str
    source_type: str


class SourceTypes(str, Enum):
    reviews = "reviews"
    news = "news"
