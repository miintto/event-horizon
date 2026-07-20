from app.infrastructure.database import AsyncScopedSession


class BasePersistenceAdapter:
    def __init__(self):
        self._scoped_session = AsyncScopedSession
