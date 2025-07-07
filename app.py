# app.py
import asyncio
import signal
from .config import Config
from .server import start_server
from .store import MetricStore
from .db_writer import DBWriter
from .migrate import main as migrate_db  
import structlog

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_log_level,
        structlog.processors.JSONRenderer()
    ]
)

logger = structlog.get_logger()

async def main():
    config = Config()
    try:
        migrate_db()  # Выполняем миграцию перед запуском сервера
        logger.info("Database migration completed")
    except Exception as e:
        logger.error(f"Database migration failed: {e}")
        return

    store = MetricStore()
    db_writer = DBWriter(store, config)

    # Запускаем сервер и писатель
    server_task = asyncio.create_task(start_server(store, config.HOST, config.PORT))
    writer_task = asyncio.create_task(db_writer.start())


    loop = asyncio.get_running_loop()
    stop = loop.create_future()

    def handle_shutdown():
        db_writer.stop()
        stop.set_result(None)

    loop.add_signal_handler(signal.SIGINT, handle_shutdown)
    loop.add_signal_handler(signal.SIGTERM, handle_shutdown)

    await stop
    server_task.cancel()
    await writer_task  
    logger.info("Server stopped")

if __name__ == "__main__":
    asyncio.run(main())