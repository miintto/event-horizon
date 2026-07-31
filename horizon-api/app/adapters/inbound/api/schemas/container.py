from datetime import datetime

from pydantic import BaseModel

from app.domain.models.container import Container, ContainerState


class ContainerResponse(BaseModel):
    id: int
    host_id: int
    workload_id: int | None = None
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

    @classmethod
    def from_domain(cls, container: Container) -> ContainerResponse:
        return cls(
            id=container.id,
            host_id=container.host_id,
            workload_id=container.workload_id,
            docker_id=container.docker_id,
            name=container.name,
            image=container.image,
            state=container.state,
            compose_project=container.compose_project,
            compose_service=container.compose_service,
            exit_code=container.exit_code,
            started_at=container.started_at,
            last_seen_at=container.last_seen_at,
            created_at=container.created_at,
        )
