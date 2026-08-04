from app.application.command.secret import (
    SecretCreateCommand,
    SecretSearchQuery,
    SecretUpdateCommand,
)
from app.application.ports.repository import SecretRepository
from app.application.ports.security import SecretCipher
from app.application.ports.usecase import SecretUseCase
from app.domain.exceptions import DuplicateSecretNameException, SecretNotFoundException
from app.domain.models import Secret
from app.infrastructure.transaction import transactional


class SecretService(SecretUseCase):
    def __init__(
        self,
        secret_repository: SecretRepository,
        secret_cipher: SecretCipher,
    ):
        self._secret_repository = secret_repository
        self._secret_cipher = secret_cipher

    @transactional
    async def get_secrets(self, query: SecretSearchQuery) -> list[Secret]:
        return await self._secret_repository.find_all(
            offset=query.offset, limit=query.size
        )

    @transactional
    async def create_secret(self, command: SecretCreateCommand) -> Secret:
        if await self._secret_repository.find_by_name(command.name):
            raise DuplicateSecretNameException

        return await self._secret_repository.save(
            Secret(
                name=command.name,
                ciphertext=self._secret_cipher.encrypt(command.value),
            )
        )

    @transactional
    async def update_secret(self, command: SecretUpdateCommand) -> Secret:
        if not (secret := await self._secret_repository.find_by_id(command.secret_id)):
            raise SecretNotFoundException

        secret.ciphertext = self._secret_cipher.encrypt(command.value)
        return await self._secret_repository.save(secret)

    @transactional
    async def delete_secret(self, secret_id: int):
        if not await self._secret_repository.find_by_id(secret_id):
            raise SecretNotFoundException

        await self._secret_repository.delete_by_id(secret_id)

    @transactional
    async def set_secret(self, name: str, value: str) -> Secret:
        ciphertext = self._secret_cipher.encrypt(value)
        if secret := await self._secret_repository.find_by_name(name):
            secret.ciphertext = ciphertext
        else:
            secret = Secret(name=name, ciphertext=ciphertext)
        return await self._secret_repository.save(secret)
