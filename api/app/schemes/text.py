from datetime import datetime

from pydantic import BaseModel


class TextItem(BaseModel):
    source_id: int
    date: datetime
    title: str
    text: str
    bank_id: str
    link: str
    comments_num: int | None = None


class Text(BaseModel):
    id: int
    link: str
    source: str
    date: datetime
    title: str
    bank_id: str
    source_id: int
    comments_num: int | None = None

    class Config:
        orm_mode = True


class TextResult(BaseModel):
    id: int
    text_sentence_id: int
    model_id: int
    result: list[float]

    class Config:
        orm_mode = True


class TextSentence(BaseModel):
    id: int
    text_id: int
    sentence: str
    sentence_num: int

    class Config:
        orm_mode = True


class PostTextItem(BaseModel):
    items: list[TextItem]
    parsed_state: str | None
    date: datetime | None


class GetTextSentences(BaseModel):
    items: list[TextSentence]


class GetTextResultItem(BaseModel):
    id: int
    text_sentence_id: int
    result: list[float]
    model_id: int


class GetTextResult(BaseModel):
    items: list[GetTextResultItem]


class PostTextResult(BaseModel):
    text_result: list[float]
    model_id: int
    text_sentence_id: int
