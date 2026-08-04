from dataclasses import dataclass
from datetime import datetime


@dataclass(kw_only=True)
class Secret:
    id: int | None = None
    name: str
    ciphertext: str
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @property
    def pk(self) -> int:
        return self.id  # type: ignore
