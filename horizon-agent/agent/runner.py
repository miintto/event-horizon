import logging
import threading
import time

from agent.buffer import MetricBuffer
from agent.collector import collect, prime_cpu
from agent.config import Settings
from agent.shipper import Shipper

logger = logging.getLogger(__name__)


class Runner:
    def __init__(self, settings: Settings, buffer: MetricBuffer, shipper: Shipper):
        self._settings = settings
        self._buffer = buffer
        self._shipper = shipper
        self._stop_event = threading.Event()

    def stop(self, *args: object):
        self._stop_event.set()

    def run(self):
        prime_cpu()
        logger.info("agent started")

        collect_interval = self._settings.collect_interval_seconds
        send_interval = self._settings.send_interval_seconds

        start = time.monotonic()
        collect_tick = 0
        next_send = start + send_interval

        while not self._stop_event.is_set():
            try:
                self._buffer.add(collect(self._settings.disk_path))
            except Exception:
                logger.exception("metric collection failed, skipping tick")

            now = time.monotonic()
            if now >= next_send:
                self._flush()
                next_send += send_interval
                if next_send <= now:
                    next_send = now + send_interval

            collect_tick += 1
            delay = start + collect_tick * collect_interval - time.monotonic()
            if delay < 0:
                missed = int(-delay // collect_interval) + 1
                collect_tick += missed
                delay = start + collect_tick * collect_interval - time.monotonic()
            self._stop_event.wait(max(0.0, delay))

        self._flush()
        logger.info("agent stopped")

    def _flush(self):
        samples = self._buffer.snapshot()
        if not samples:
            return
        if self._shipper.send(samples):
            self._buffer.remove(samples)
            logger.info("sent %d datapoints", len(samples))
        else:
            logger.warning("send failed, %d datapoints buffered", len(self._buffer))
