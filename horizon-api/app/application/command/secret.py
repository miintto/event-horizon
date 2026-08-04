from dataclasses import dataclass


@dataclass
class SecretSearchQuery:
    page: int
    size: int

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size


@dataclass
class SecretCreateCommand:
    name: str
    value: str


@dataclass
class SecretUpdateCommand:
    secret_id: int
    value: str
