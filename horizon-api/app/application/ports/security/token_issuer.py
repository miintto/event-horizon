from abc import ABC, abstractmethod


class TokenIssuer(ABC):
    @abstractmethod
    def issue(self, user_id: int) -> str: ...

    @abstractmethod
    def resolve(self, token: str) -> int: ...
