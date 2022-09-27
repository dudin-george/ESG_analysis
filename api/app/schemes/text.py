from datetime import datetime

from pydantic import BaseModel


class TextItem(BaseModel):
    source: str
    date: datetime
    title: str
    text: str
    bank_id: str
    link: str
    comments_num: int | None = None
    user_id: str | None = None
    rating: int | None = None


class PostTextItem(BaseModel):
    items: list[TextItem]
    parsed_state: str | None
    date: datetime | None


class TextSentenceItem(BaseModel):
    id: int
    sentence: str
    review_id: int


class GetTextSentences(BaseModel):
    items: list[TextSentenceItem]


class GetTextResultItem(BaseModel):
    id: int
    text_sentence_id: int
    result: list[float]
    model_id: int


class PostTextResult(BaseModel):
    text_result: list[float]
    model: int
    text_sentence_id: int
