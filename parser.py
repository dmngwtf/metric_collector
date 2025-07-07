import struct
from datetime import datetime
from .models import Metric

class MetricParser:
    @staticmethod
    def parse(data: bytes) -> Metric:
        try:
            # Распаковываем timestamp (uint64_t, 8 байт, big-endian)
            timestamp = struct.unpack(">Q", data[:8])[0]
            # Длина имени метрики (uint8_t, 1 байт)
            name_length = struct.unpack("B", data[8:9])[0]
            # Имя метрики (utf-8, переменной длины)
            name = data[9:9 + name_length].decode("utf-8")
            # Значение метрики (float64, 8 байт, big-endian)
            value = struct.unpack(">d", data[9 + name_length:])[0]
            # Конвертируем timestamp в datetime
            dt = datetime.fromtimestamp(timestamp)
            return Metric(timestamp=dt, name=name, value=value)
        except (struct.error, UnicodeDecodeError) as e:
            raise ValueError(f"Failed to parse metric: {e}")