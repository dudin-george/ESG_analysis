from pydantic import BaseModel


class GetModel(BaseModel):
    model_name: str
    id: int
    model_type: str


class PostModel(BaseModel):
    model_name: str
    model_type: str


class PostModelResponse(BaseModel):
    model_id: int
