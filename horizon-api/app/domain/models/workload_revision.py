from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True, kw_only=True)
class EnvVar:
    name: str
    value: str


@dataclass(frozen=True, kw_only=True)
class SecretRef:
    name: str
    ref: str


@dataclass(frozen=True, kw_only=True)
class PortBinding:
    container_port: int
    host_port: int | None = None
    protocol: str = "tcp"


@dataclass(frozen=True, kw_only=True)
class Mount:
    type: str
    source: str
    target: str
    read_only: bool = False


@dataclass(frozen=True, kw_only=True)
class RestartPolicy:
    name: str
    max_retry: int = 0


@dataclass(frozen=True, kw_only=True)
class Healthcheck:
    test: list[str]
    interval_secs: int | None = None
    timeout_secs: int | None = None
    retries: int | None = None


@dataclass(frozen=True, kw_only=True)
class Network:
    mode: str | None = None
    names: list[str] = field(default_factory=list)


@dataclass(frozen=True, kw_only=True)
class LogConfig:
    driver: str
    options: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True, kw_only=True)
class ContainerSpec:
    command: list[str] | None = None
    entrypoint: list[str] | None = None
    env: list[EnvVar] = field(default_factory=list)
    secrets: list[SecretRef] = field(default_factory=list)
    ports: list[PortBinding] = field(default_factory=list)
    mounts: list[Mount] = field(default_factory=list)
    restart_policy: RestartPolicy | None = None
    healthcheck: Healthcheck | None = None
    labels: dict[str, str] = field(default_factory=dict)
    network: Network | None = None
    log: LogConfig | None = None


@dataclass(kw_only=True)
class WorkloadRevision:
    id: int | None = None
    workload_id: int
    revision: int
    image: str
    cpu_limit: Decimal | None = None
    memory_limit: int | None = None
    spec: ContainerSpec
    created_at: datetime | None = None

    @property
    def pk(self) -> int:
        return self.id  # type: ignore
