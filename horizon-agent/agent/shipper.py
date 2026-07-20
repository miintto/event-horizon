import logging
from dataclasses import asdict
from uuid import UUID

import httpx

from agent.collector import MetricSample

logger = logging.getLogger(__name__)


class Shipper:
    def __init__(
        self, server_url: str, agent_uuid: UUID, hostname: str, timeout: float
    ):
        self._url = f"{server_url.rstrip('/')}/api/metrics/hosts"
        self._agent_uuid = agent_uuid
        self._hostname = hostname
        self._timeout = timeout

    def send(self, samples: list[MetricSample]) -> bool:
        payload = {
            "agent_uuid": str(self._agent_uuid),
            "hostname": self._hostname,
            "datapoints": [self._to_datapoint(sample) for sample in samples],
        }
        try:
            response = httpx.post(self._url, json=payload, timeout=self._timeout)
        except httpx.HTTPError as exc:
            logger.warning("metric send failed: %s", exc)
            return False

        if response.is_success:
            return True
        if httpx.codes.BAD_REQUEST <= response.status_code < 500:
            logger.error(
                "metric batch rejected (%s), dropping: %s",
                response.status_code,
                response.text,
            )
            return True

        logger.warning("metric send failed: status %s", response.status_code)
        return False

    @staticmethod
    def _to_datapoint(sample: MetricSample) -> dict:
        datapoint = asdict(sample)
        datapoint["collected_at"] = sample.collected_at.isoformat()
        return datapoint
