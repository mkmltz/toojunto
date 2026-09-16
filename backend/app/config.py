from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://toojunto:toojunto_dev@localhost:5432/toojunto"
    jwt_secret: str = "change-me-in-development"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
