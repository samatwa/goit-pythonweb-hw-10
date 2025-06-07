from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    app_title: str = "Contacts API"
    app_description: str = "REST API для управління контактами"
    app_version: str = "1.0.0"
    debug: bool = False

    class Config:
        env_file = ".env"


settings = Settings()
