from datetime import datetime

from pydantic import BaseModel


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
