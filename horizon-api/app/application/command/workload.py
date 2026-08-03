from dataclasses import dataclass, field
from decimal import Decimal

from app.domain.models import ContainerSpec


@dataclass
class RevisionDefinition:
    image: str
    cpu_limit: Decimal | None = None
    memory_limit: int | None = None
    spec: ContainerSpec = field(default_factory=ContainerSpec)


@dataclass
class WorkloadCreateCommand:
    name: str
    definition: RevisionDefinition


@dataclass
class RevisionCreateCommand:
    workload_id: int
    definition: RevisionDefinition
