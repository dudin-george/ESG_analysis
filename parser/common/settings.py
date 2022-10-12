from pydantic import AnyHttpUrl, BaseSettings, Field, PostgresDsn


class Settings(BaseSettings):
    database_url: PostgresDsn = Field(env="DATABASE_URL")
    api_url: AnyHttpUrl = Field(env="API_URL")
    logger_level: int = Field(env="LOGGER_LEVEL", default=10)

def get_settings():
    return Settings()
