from pathlib import Path
from uuid import UUID, uuid4


def load_or_create_agent_uuid(path: Path) -> UUID:
    if path.exists():
        return UUID(path.read_text().strip())

    path.parent.mkdir(parents=True, exist_ok=True)
    agent_uuid = uuid4()
    path.write_text(str(agent_uuid))
    return agent_uuid
