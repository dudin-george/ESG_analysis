from pydantic import BaseSettings, Field, AnyHttpUrl, PostgresDsn


class Settings(BaseSettings):
    database_url: PostgresDsn = Field(env="DATABASE_URL")
    api_url: AnyHttpUrl = Field(env="API_URL")
