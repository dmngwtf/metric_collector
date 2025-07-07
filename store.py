# store.py
from collections import defaultdict
import asyncio
from .models import Metric

class MetricStore:
    def __init__(self):
        self._store = defaultdict(list)  # Хранилище: {metric_name: [Metric]}
        self._lock = asyncio.Lock()

    async def add(self, metric: Metric):
        async with self._lock:
            self._store[metric.name].append(metric)

    async def get_all(self) -> dict:
        async with self._lock:
            # Возвращаем копию данных и очищаем хранилище
            result = self._store.copy()
            self._store.clear()
            return result