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


class GetModel(BaseModel):
    model_name: str
    id: int
    model_type: str


class PostModel(BaseModel):
    model_name: str
    model_type: str


class PostModelResponse(BaseModel):
    model_id: int


class GetTextResultItem(BaseModel):
    id: int
    text_sentence_id: int
    result: list[float]
    model_id: int


class PostTextResult(BaseModel):
    text_result: list[float]
    model: int
    text_sentence_id: int


class GetSourceItem(BaseModel):
    id: int
    site: str
    source_type_id: int
    source_type: str
    parser_state: str | None
    last_update: datetime | None


class GetSource(BaseModel):
    items: list[GetSourceItem]


class CreateSource(BaseModel):
    site: str
    source_type: str


class PostSourceResponse(BaseModel):
    source_id: int


class GetSourceTypesItem(BaseModel):
    id: int
    name: str


class GetSourceTypes(BaseModel):
    items: list[GetSourceTypesItem]


class Bank(BaseModel):
    id: str
    bank_name: str
