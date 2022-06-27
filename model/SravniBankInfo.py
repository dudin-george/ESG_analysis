from sqlmodel import VARCHAR, Column, Field, SQLModel


class SravniBankInfo(SQLModel, table=True):
    id: str = Field(default=None, primary_key=True, max_length=30, index=True)
    bank_name: str = Field(sa_column=Column("bank_name", VARCHAR, unique=True))
    alias: str
