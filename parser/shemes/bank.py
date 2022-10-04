from datetime import datetime

from pydantic import BaseModel


class Bank(BaseModel):
    id: str
    bank_name: str


class BankiRuItem(BaseModel):
    bank_id: int
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
    bank_id: int

    class Config:
        orm_mode = True


class SourceRequest(BaseModel):
    site: str
    source_type: str


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
    bank_id: str
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
