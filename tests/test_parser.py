# tests/test_parser.py
import pytest
from metric_collector.parser import MetricParser
from metric_collector.models import Metric
from datetime import datetime

@pytest.mark.asyncio
async def test_parse_valid_metric():
    # timestamp=1697059200 (2023-10-12 00:00:00), name="metric", value=3.1415927
    data = b"\x00\x00\x01\x88\xD2\xE9\xA0\x00\x06metric\x40\x49\x0F\xDB\x00\x00\x00\x00"
    metric = MetricParser.parse(data)
    assert metric.name == "metric"
    assert metric.value == pytest.approx(3.1415927)
    assert metric.timestamp == datetime.fromtimestamp(1697059200)

@pytest.mark.asyncio
async def test_parse_invalid_data():
    with pytest.raises(ValueError):
        MetricParser.parse(b"\x00" * 10)  # Недостаточно данных