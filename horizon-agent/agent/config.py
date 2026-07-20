from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    server_url: str
    collect_interval_seconds: int = Field(default=10, gt=0)
    send_interval_seconds: int = Field(default=60, gt=0)
    agent_id_path: str = "/var/lib/horizon-agent/agent_id"
    disk_path: str = "/"
    http_timeout_seconds: int = Field(default=10, gt=0)
    max_buffer_size: int = Field(default=2880, ge=1)

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}
