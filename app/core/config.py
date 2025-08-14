from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Secure Tracker API"
    ENV: str = "development"
    DB_NAME: str = "secure_tracker"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "password"

    class Config:
        env_file = ".env"


settings = Settings()
