from enum import StrEnum


class HostMetricKind(StrEnum):
    CPU_USAGE = "cpu_usage"
    MEMORY_USED = "memory_used"
    MEMORY_TOTAL = "memory_total"
    DISK_USED = "disk_used"
    DISK_TOTAL = "disk_total"
    LOAD_AVG_1 = "load_avg_1"
    LOAD_AVG_5 = "load_avg_5"
    LOAD_AVG_15 = "load_avg_15"
    NET_RX_RATE = "net_rx_rate"
    NET_TX_RATE = "net_tx_rate"


class ContainerMetricKind(StrEnum):
    CPU_USAGE = "cpu_usage"
    CPU_THROTTLED_TIME = "cpu_throttled_time"
    MEMORY_USED = "memory_used"
    MEMORY_LIMIT = "memory_limit"
    BLOCK_READ_RATE = "block_read_rate"
    BLOCK_WRITE_RATE = "block_write_rate"
    NET_RX_RATE = "net_rx_rate"
    NET_TX_RATE = "net_tx_rate"
    PIDS = "pids"


class AggregateInterval(StrEnum):
    ONE_MINUTE = "1m"
    FIVE_MINUTES = "5m"
    TEN_MINUTES = "10m"
    ONE_HOUR = "1h"

    @property
    def seconds(self) -> int:
        match self:
            case AggregateInterval.ONE_MINUTE:
                return 60
            case AggregateInterval.FIVE_MINUTES:
                return 300
            case AggregateInterval.TEN_MINUTES:
                return 600
            case AggregateInterval.ONE_HOUR:
                return 3600
            case _:
                raise ValueError("Invalid Interval")

    @property
    def max_range(self) -> int:
        match self:
            case AggregateInterval.ONE_MINUTE:
                return 3 * 3600  # 3 hours
            case AggregateInterval.FIVE_MINUTES:
                return 16 * 3600  # 16 hours
            case AggregateInterval.TEN_MINUTES:
                return 36 * 3600  # 36 hours
            case AggregateInterval.ONE_HOUR:
                return 8 * 24 * 3600  # 8 days
            case _:
                raise ValueError("Invalid Interval")
