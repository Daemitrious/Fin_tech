from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "payment-service"
    environment: str = "local"
    api_v1_prefix: str = "/api/v1"
    api_key: str = "super-secret-api-key"
    database_url: str = "postgresql+asyncpg://payment:payment@postgres:5432/payments"
    alembic_database_url: str = "postgresql+psycopg://payment:payment@postgres:5432/payments"
    rabbitmq_url: str = "amqp://guest:guest@rabbitmq:5672/"
    payments_exchange: str = "payments"
    payments_new_queue: str = "payments.new"
    payments_dlq: str = "payments.dlq"
    outbox_publish_interval_sec: int = 1
    webhook_timeout_sec: int = 5
    max_webhook_attempts: int = 3
    payment_processing_min_delay_sec: int = 2
    payment_processing_max_delay_sec: int = 5


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
