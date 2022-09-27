from datetime import datetime

from pydantic import BaseModel


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
