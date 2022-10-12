from pydantic import BaseSettings, Field, PostgresDsn


class Settings(BaseSettings):
    database_url: PostgresDsn = Field(
        env="DATABASE_URL", default=PostgresDsn("postgresql+psycopg2://myusername:mypassword@localhost/database")
    )
    echo: bool = Field(env="ECHO", default=False)
    # broker_url: AmqpDsn = Field(env="BROKER_URL")
