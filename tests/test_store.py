# tests/test_store.py
import pytest
from metric_collector.store import MetricStore
from metric_collector.models import Metric
from datetime import datetime

@pytest.mark.asyncio
async def test_store_add_and_get():
    store = MetricStore()
    metric = Metric(timestamp=datetime.now(), name="test", value=42.0)
    await store.add(metric)
    metrics = await store.get_all()
    assert metrics["test"] == [metric]
    assert len(await store.get_all()) == 0  # Проверяем очистку