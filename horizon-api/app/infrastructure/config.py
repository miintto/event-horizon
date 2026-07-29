from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_env: str = "local"

    cors_origins: list[str] = ["*"]

    ingest_api_key: str

    db_host: str
    db_port: int = 5432
    db_name: str
    db_user: str
    db_password: str

    db_pool_size: int = 10
    db_max_overflow: int = 10

    container_stale_after_secs: int = 300

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()  # type: ignore[call-arg]
