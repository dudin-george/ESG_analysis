from pydantic import AnyHttpUrl, BaseSettings, Field, PostgresDsn


class Settings(BaseSettings):
    database_url: PostgresDsn = Field(env="DATABASE_URL")
    api_url: AnyHttpUrl = Field(env="API_URL")
    logger_level: int = Field(env="LOGGER_LEVEL", default=10)
    vk_token: str | None = Field(env="VK_TOKEN")
    selenium_hub: AnyHttpUrl | None = Field(env="SELENIUM_HUB")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def get_settings() -> Settings:
    return Settings()
