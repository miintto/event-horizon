from cryptography.fernet import Fernet, InvalidToken, MultiFernet

from app.application.ports.security import SecretCipher
from app.domain.exceptions import SecretDecryptionException


class FernetCipher(SecretCipher):
    def __init__(self, key: str, previous_key: str = ""):
        if not key:
            raise ValueError("`secret_encryption_key` is empty")
        keys = [Fernet(key)]
        if previous_key:
            keys.append(Fernet(previous_key))
        self._fernet = MultiFernet(keys)

    def encrypt(self, plaintext: str) -> str:
        return self._fernet.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        try:
            return self._fernet.decrypt(ciphertext.encode()).decode()
        except InvalidToken:
            raise SecretDecryptionException
