from collections import deque

from agent.collector import MetricSample


class MetricBuffer:
    def __init__(self, max_size: int):
        self._items: deque[MetricSample] = deque(maxlen=max_size)

    def add(self, sample: MetricSample):
        self._items.append(sample)

    def snapshot(self) -> list[MetricSample]:
        return list(self._items)

    def remove(self, sent: list[MetricSample]):
        sent_ids = {id(sample) for sample in sent}
        remaining = [sample for sample in self._items if id(sample) not in sent_ids]
        self._items.clear()
        self._items.extend(remaining)

    def __len__(self) -> int:
        return len(self._items)
