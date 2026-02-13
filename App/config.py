from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


class BaseConfig(BaseSettings):
    ENV_STATE: Optional[str] = None

    # Load environment variables from a .env file using new Pydantic v2 syntax
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class GlobalConfig(BaseConfig):
    OPENROUTER_API_KEY: str
    USDA_API_KEY: str
    TELEGRAM_BOT_TOKEN: str
    DATABASE_URL: str = "sqlite:///nutrition_logs.db"
    DB_FORCE_ROLL_BACK: bool = False

    # PostgreSQL connection fields
    POSTGRE_USER: str
    POSTGRE_PASSWORD: str
    POSTGRE_HOST: str = "127.0.0.1"
    POSTGRE_NAME: str = "food_db"
    POSTGRE_PORT: int = 5432


class DevConfig(GlobalConfig):
    model_config = SettingsConfigDict(env_prefix="DEV_")


class TestConfig(GlobalConfig):
    model_config = SettingsConfigDict(env_prefix="TEST_")


class ProdConfig(GlobalConfig):
    model_config = SettingsConfigDict(env_prefix="PROD_")


# lru_cache to avoid reloading config multiple times
@lru_cache()
def get_config(env_state: str):
    configs = {
        "dev": DevConfig,
        "test": TestConfig,
        "prod": ProdConfig,
    }
    return configs[env_state]()


config = get_config(BaseConfig().ENV_STATE)


# PostgreSQL database connection
class DatabaseConfig:
    """Database configuration class to manage database connection settings."""

    DRIVER = "postgresql+psycopg2"
    ECHO = False  # Set to False in production

    @classmethod
    def get_database_url(cls) -> URL:
        """Constructs the database URL from environment variables."""
        return URL.create(
            drivername=cls.DRIVER,
            username=config.POSTGRE_USER,
            password=config.POSTGRE_PASSWORD,
            host=config.POSTGRE_HOST,
            database=config.POSTGRE_NAME,
            port=config.POSTGRE_PORT,
        )
