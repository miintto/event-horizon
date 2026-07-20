import logging
import signal
from pathlib import Path
from socket import gethostname

from agent.buffer import MetricBuffer
from agent.config import Settings
from agent.identity import load_or_create_agent_uuid
from agent.runner import Runner
from agent.shipper import Shipper


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    settings = Settings()  # type: ignore[call-arg]
    agent_uuid = load_or_create_agent_uuid(Path(settings.agent_id_path))
    hostname = gethostname()

    buffer = MetricBuffer(settings.max_buffer_size)
    shipper = Shipper(
        settings.server_url,
        agent_uuid,
        hostname,
        settings.http_timeout_seconds,
    )
    runner = Runner(settings, buffer, shipper)

    signal.signal(signal.SIGTERM, runner.stop)
    signal.signal(signal.SIGINT, runner.stop)

    runner.run()


if __name__ == "__main__":
    main()
