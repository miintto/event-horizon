from dataclasses import dataclass
from datetime import datetime, timezone

import psutil


@dataclass
class MetricSample:
    collected_at: datetime
    cpu_usage: float
    memory_used: int
    memory_total: int
    disk_used: int
    disk_total: int
    net_rx: int
    net_tx: int
    load_avg_1: float | None = None
    load_avg_5: float | None = None
    load_avg_15: float | None = None


def prime_cpu():
    psutil.cpu_percent(interval=None)


def collect(disk_path: str) -> MetricSample:
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage(disk_path)
    net = psutil.net_io_counters()

    load_avg_1 = load_avg_5 = load_avg_15 = None
    try:
        load_avg_1, load_avg_5, load_avg_15 = psutil.getloadavg()
    except (OSError, AttributeError):
        pass

    return MetricSample(
        collected_at=datetime.now(timezone.utc),
        cpu_usage=psutil.cpu_percent(interval=None),
        memory_used=memory.used,
        memory_total=memory.total,
        disk_used=disk.used,
        disk_total=disk.total,
        net_rx=net.bytes_recv,
        net_tx=net.bytes_sent,
        load_avg_1=load_avg_1,
        load_avg_5=load_avg_5,
        load_avg_15=load_avg_15,
    )
