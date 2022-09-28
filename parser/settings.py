from pydantic import BaseSettings, Field, HttpUrl, PostgresDsn


class Settings(BaseSettings):
    database_url: PostgresDsn = Field(env="DATABASE_URL")
    api_url: HttpUrl = Field(env="API_URL")
