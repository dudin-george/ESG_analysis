from pydantic import AmqpDsn, BaseSettings, Field, PostgresDsn


class Settings(BaseSettings):
    database_url: PostgresDsn = Field(env="DATABASE_URL")
    # broker_url: AmqpDsn = Field(env="BROKER_URL")
