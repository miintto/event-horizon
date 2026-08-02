from dataclasses import dataclass
from datetime import datetime


@dataclass(kw_only=True)
class Workload:
    id: int | None = None
    name: str
    current_revision_id: int | None = None
    created_at: datetime | None = None
