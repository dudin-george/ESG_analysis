from pydantic import BaseSettings, Field, PostgresDsn


class Settings(BaseSettings):
    database_url: PostgresDsn = Field(
        env="DATABASE_URL"
    )
    echo: bool = Field(env="ECHO", default=False)
    # broker_url: AmqpDsn = Field(env="BROKER_URL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
