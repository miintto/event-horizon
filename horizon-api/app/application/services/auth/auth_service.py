from app.application.command.auth import LoginCommand, RegisterCommand, TokenResult
from app.application.ports.repository import UserRepository
from app.application.ports.security import PasswordHasher, TokenProvider
from app.application.ports.usecase import AuthUseCase
from app.domain.exceptions import (
    DuplicateEmailException,
    InactiveUserException,
    InvalidCredentialsException,
)
from app.domain.models import User, UserRole
from app.infrastructure.transaction import transactional


class AuthService(AuthUseCase):
    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
        token_provider: TokenProvider,
        expire_secs: int,
    ):
        self._user_repository = user_repository
        self._password_hasher = password_hasher
        self._token_provider = token_provider
        self._expire_secs = expire_secs

    @transactional
    async def register(self, command: RegisterCommand) -> TokenResult:
        user = await self._create_user(
            name=command.name,
            email=command.email,
            password=command.password,
            role=command.role,
        )
        return self._issue(user)

    @transactional
    async def login(self, command: LoginCommand) -> TokenResult:
        user = await self._user_repository.find_by_email(command.email)
        if not user or not self._password_hasher.verify(
            command.password, user.password_hash
        ):
            raise InvalidCredentialsException
        elif not user.is_active:
            raise InactiveUserException

        return self._issue(user)

    @transactional
    async def create_admin(self, name: str | None, email: str, password: str) -> User:
        return await self._create_user(
            name=name,
            email=email,
            password=password,
            role=UserRole.ADMIN,
        )

    async def _create_user(
        self, name: str | None, email: str, password: str, role: UserRole
    ) -> User:
        if await self._user_repository.find_by_email(email):
            raise DuplicateEmailException

        return await self._user_repository.save(
            User(
                name=name,
                email=email,
                password_hash=self._password_hasher.hash(password),
                role=role,
            )
        )

    def _issue(self, user: User) -> TokenResult:
        return TokenResult(
            access_token=self._token_provider.encode(user.pk, user.role),
            expires_in=self._expire_secs,
        )
