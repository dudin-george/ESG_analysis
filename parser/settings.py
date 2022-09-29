from pydantic import AnyHttpUrl, BaseSettings, Field, PostgresDsn


class Settings(BaseSettings):
    database_url: PostgresDsn = Field(env="DATABASE_URL")
    api_url: AnyHttpUrl = Field(env="API_URL")
