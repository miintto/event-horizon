from dataclasses import asdict
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    DateTime,
    Index,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.models import (
    ContainerSpec,
    EnvVar,
    Healthcheck,
    LogConfig,
    Mount,
    Network,
    PortBinding,
    RestartPolicy,
    SecretRef,
    WorkloadRevision,
)
from app.infrastructure.database import Base

_EMPTY = (None, [], {})


class WorkloadRevisionModel(Base):
    __tablename__ = "workload_revision"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workload_id: Mapped[int] = mapped_column(Integer, nullable=False)
    revision: Mapped[int] = mapped_column(Integer, nullable=False)
    image: Mapped[str] = mapped_column(String(255), nullable=False)
    cpu_limit: Mapped[Decimal | None] = mapped_column(Numeric(6, 3), nullable=True)
    memory_limit: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    spec: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint("workload_id", "revision", name="uq_workload_revision"),
        Index("ix_workload_revision_workload_id", "workload_id"),
    )

    def to_domain(self) -> WorkloadRevision:
        return WorkloadRevision(
            id=self.id,
            workload_id=self.workload_id,
            revision=self.revision,
            image=self.image,
            cpu_limit=self.cpu_limit,
            memory_limit=self.memory_limit,
            spec=self._spec_from_json(self.spec),
            created_at=self.created_at,
        )

    @classmethod
    def from_domain(cls, revision: WorkloadRevision) -> WorkloadRevisionModel:
        kwargs = {
            "workload_id": revision.workload_id,
            "revision": revision.revision,
            "image": revision.image,
            "cpu_limit": revision.cpu_limit,
            "memory_limit": revision.memory_limit,
            "spec": {k: v for k, v in asdict(revision.spec).items() if v not in _EMPTY},
        }
        if revision.id is not None:
            kwargs["id"] = revision.id
        if revision.created_at is not None:
            kwargs["created_at"] = revision.created_at
        return cls(**kwargs)

    def _spec_from_json(self, raw: dict) -> ContainerSpec:
        restart_policy = raw.get("restart_policy")
        healthcheck = raw.get("healthcheck")
        network = raw.get("network")
        log = raw.get("log")
        return ContainerSpec(
            command=raw.get("command"),
            entrypoint=raw.get("entrypoint"),
            env=[EnvVar(**e) for e in raw.get("env", [])],
            secrets=[SecretRef(**s) for s in raw.get("secrets", [])],
            ports=[PortBinding(**p) for p in raw.get("ports", [])],
            mounts=[Mount(**m) for m in raw.get("mounts", [])],
            restart_policy=RestartPolicy(**restart_policy) if restart_policy else None,
            healthcheck=Healthcheck(**healthcheck) if healthcheck else None,
            labels=raw.get("labels", {}),
            network=Network(**network) if network else None,
            log=LogConfig(**log) if log else None,
        )
