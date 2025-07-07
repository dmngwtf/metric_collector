# db_writer.py
import asyncio
import psycopg2
from .store import MetricStore
from .config import Config
import structlog

logger = structlog.get_logger()

class DBWriter:
    def __init__(self, store: MetricStore, config: Config):
        self.store = store
        self.config = config
        self.running = False

    async def start(self):
        self.running = True
        while self.running:
            await asyncio.sleep(self.config.DB_FLUSH_INTERVAL)
            await self.flush()

    async def flush(self):
        metrics = await self.store.get_all()
        if not metrics:
            return

        try:
            conn = psycopg2.connect(**self.config.DB_CONNECTION)
            cursor = conn.cursor()
            for metric_name, metric_list in metrics.items():
                values = [
                    (m.timestamp, m.name, m.value)
                    for m in metric_list
                ]
                cursor.executemany(
                    "INSERT INTO metrics (timestamp, metric_name, value) VALUES (%s, %s, %s)",
                    values
                )
            conn.commit()
            logger.info(f"Flushed {sum(len(v) for v in metrics.values())} metrics to DB")
        except Exception as e:
            logger.error(f"Failed to flush metrics: {e}")
        finally:
            cursor.close()
            conn.close()

    def stop(self):
        self.running = False