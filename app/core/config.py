from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Secure Tracker API"
    # DATABASE_URL: str
    ENV: str = "development"

    class Config:
        env_file = ".env"


settings = Settings()
