from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class ContainerState(StrEnum):
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    RESTARTING = "restarting"
    REMOVING = "removing"
    EXITED = "exited"
    DEAD = "dead"


@dataclass(kw_only=True)
class Container:
    id: int | None = None
    host_id: int
    docker_id: str
    name: str
    image: str
    state: ContainerState
    compose_project: str | None = None
    compose_service: str | None = None
    exit_code: int | None = None
    started_at: datetime | None = None
    last_seen_at: datetime | None = None
    created_at: datetime | None = None
