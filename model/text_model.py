from sqlmodel import Field, SQLModel


class TextModels(SQLModel, table=True):
    text_id: int = Field(default=None, foreign_key="textresult.id", primary_key=True)
    model_id: int = Field(default=None, foreign_key="models.id", primary_key=True)
