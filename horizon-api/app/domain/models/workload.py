from dataclasses import dataclass
from datetime import datetime


@dataclass(kw_only=True)
class Workload:
    id: int | None = None
    name: str
    created_at: datetime | None = None
