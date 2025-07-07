# models.py
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Metric:
    timestamp: datetime
    name: str
    value: float