import argparse
import asyncio
import getpass

from app.adapters.inbound.api.dependencies import get_auth_service
from app.domain.exceptions import APIException
from app.infrastructure.database import engine


def main():
    parser = argparse.ArgumentParser(prog="horizon")
    subparsers = parser.add_subparsers(dest="command", required=True)

    create_admin = subparsers.add_parser("create-admin", help="Create an ADMIN user")
    create_admin.add_argument("--email", required=True)
    create_admin.add_argument("--name")

    args = parser.parse_args()
    if args.command == "create-admin":
        asyncio.run(_create_admin(args.name, args.email))


async def _create_admin(name: str | None, email: str) -> None:
    password = _prompt_password()

    service = await get_auth_service()
    try:
        user = await service.create_admin(name, email, password)
    except APIException as e:
        raise SystemExit(f"✗ {e.detail}")
    finally:
        await engine.dispose()

    print(f"✓ admin created (id={user.id}, email={user.email}, name={user.name})")


def _prompt_password() -> str:
    password = getpass.getpass("Password: ")
    if len(password) < 8:
        raise SystemExit("✗ Password must be at least 8 characters")
    if len(password.encode()) > 32:
        raise SystemExit("✗ Password must not exceed 32 bytes")
    if password != getpass.getpass("Password (again): "):
        raise SystemExit("✗ Passwords do not match")
    return password
