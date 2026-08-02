from abc import ABC, abstractmethod


class PasswordHasher(ABC):
    @abstractmethod
    def hash(self, raw: str) -> str: ...

    @abstractmethod
    def verify(self, raw: str, hashed: str) -> bool: ...
