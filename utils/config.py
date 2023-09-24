from functools import lru_cache

from dotenv import find_dotenv, load_dotenv
from pydantic import RedisDsn, field_validator
from pydantic_core.core_schema import FieldValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file_encoding='utf_8',
    )

    # services
    BET_SERVICE_NAME: str
    LP_SERVICE_NAME: str
    BET_MAKER_PORT: int
    LINE_PROVIDER_PORT: int

    # redis
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: str = "0"
    REDIS_URL: RedisDsn | None = None

    @field_validator("REDIS_URL", mode='before')  # noqa
    @classmethod
    def construct_db_url(cls, v, info: FieldValidationInfo):
        if isinstance(v, str):
            return v
        return RedisDsn.build(
            scheme="redis",
            host=info.data.get("REDIS_HOST", "localhost"),
            port=info.data.get("REDIS_PORT", "6379"),
            path=info.data.get("REDIS_DB", "0"),
        )


@lru_cache
def get_settings():
    find_dotenv()
    load_dotenv()
    return Settings()
