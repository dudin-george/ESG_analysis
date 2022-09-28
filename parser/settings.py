from pydantic import BaseSettings, PostgresDsn, Field, HttpUrl


class Settings(BaseSettings):
    database_url: PostgresDsn = Field(env="DATABASE_URL")
    api_url: HttpUrl = Field(env="API_URL")