import functools

from app.infrastructure.database import AsyncScopedSession


def transactional(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        session = AsyncScopedSession()
        already_active = session.in_transaction()
        try:
            result = await func(*args, **kwargs)
            if not already_active:
                await session.commit()
            return result
        except Exception:
            if not already_active:
                await session.rollback()
            raise
        finally:
            if not already_active:
                await AsyncScopedSession.remove()

    return wrapper
