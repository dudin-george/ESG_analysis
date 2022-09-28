from datetime import datetime

from pydantic import BaseModel


class Bank(BaseModel):
    id: str
    bank_name: str


class BankiRuItem(BaseModel):
    id: str
    bank_name: str
    reviews_url: str


class Source(BaseModel):
    site: str
    source_type: str


class SourceResponse(BaseModel):
    id: int
    site: str
    source_type_id: int
    parser_state: str | None
    last_update: datetime | None


class Text(BaseModel):
    source_id: int
    date: datetime
    title: str
    text: str
    bank_id: str
    link: str
    comments_num: int | None


class TextRequest(BaseModel):
    items: list[Text]
    parsed_state: str | None = None
    last_update: datetime | None = None
