from datetime import datetime

from pydantic import BaseModel


class Bank(BaseModel):
    id: str
    bank_name: str


class BankiRuItem(BaseModel):
    bank_id: str
    bank_name: str
    reviews_url: str

    class Config:
        orm_mode = True


class SravniRuItem(BaseModel):
    sravni_id: str
    sravni_old_id: int
    alias: str
    bank_name: str
    bank_full_name: str
    bank_official_name: str
    bank_id: str

    class Config:
        orm_mode = True


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
