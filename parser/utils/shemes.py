import re
from datetime import datetime

from pydantic import BaseModel, validator


class Bank(BaseModel):
    id: int
    bank_name: str


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
    comments_num: int | None

    @validator("text")
    def text_validator(cls, v: str) -> str:
        s = re.sub("[\xa0\n\t]", " ", v)
        return re.sub("<[^>]*>", "", s).strip()

    @validator("date")
    def date_validator(cls, v: str | datetime) -> datetime:
        if type(v) == str:
            return datetime.strptime(v, "%Y-%m-%d %H:%M:%S")
        return v

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
