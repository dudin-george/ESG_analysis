from datetime import datetime

from pydantic import BaseModel


class Source(BaseModel):
    id: int
    site: str
    source_type_id: int
    parser_state: str | None
    last_update: datetime | None

    class Config:
        orm_mode = True


class GetSourceItem(Source):
    source_type: str


class GetSource(BaseModel):
    items: list[Source]


class CreateSource(BaseModel):
    site: str
    source_type: str


class PostSourceResponse(BaseModel):
    source_id: int


class SourceTypes(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class GetSourceTypes(BaseModel):
    items: list[SourceTypes]
