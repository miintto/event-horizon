from dataclasses import dataclass, field


@dataclass
class NetworkSearchQuery:
    page: int
    size: int

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size


@dataclass
class NetworkCreateCommand:
    name: str
    driver: str
    options: dict[str, str] = field(default_factory=dict)


@dataclass
class NetworkAttachCommand:
    workload_id: int
    network_id: int
    alias: str | None = None
