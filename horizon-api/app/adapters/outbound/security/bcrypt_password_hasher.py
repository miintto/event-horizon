from bcrypt import checkpw, gensalt, hashpw

from app.application.ports.security.password_hasher import PasswordHasher


class BcryptPasswordHasher(PasswordHasher):
    def hash(self, raw_password: str) -> str:
        return hashpw(raw_password.encode(), gensalt(rounds=12)).decode()

    def verify(self, raw_password: str, hashed: str) -> bool:
        try:
            return checkpw(raw_password.encode(), hashed.encode())
        except ValueError:
            return False
