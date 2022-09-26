from pydantic import BaseSettings, Field, PostgresDsn


class Settings(BaseSettings):
    database_url: PostgresDsn = Field(env="DATABASE_URL")
