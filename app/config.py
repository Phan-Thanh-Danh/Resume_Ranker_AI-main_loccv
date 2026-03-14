from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Resume Ranking API"
    APP_ENV: str = "development"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    MAX_FILE_SIZE_MB: int = 10
    TOP_K_DEFAULT: int = 10

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()
