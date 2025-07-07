# server.py
import asyncio
from .parser import MetricParser
from .store import MetricStore
import structlog
import struct
logger = structlog.get_logger()

async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter, store: MetricStore):
    addr = writer.get_extra_info("peername")
    logger.info(f"New connection from {addr}")

    try:
        while True:
            # Читаем заголовок: 8 (timestamp) + 1 (name_length) = 9 байт
            header = await reader.readexactly(9)
            timestamp = struct.unpack(">Q", header[:8])[0]
            name_length = header[8]

            # Читаем имя метрики и значение
            name_data = await reader.readexactly(name_length)
            value_data = await reader.readexactly(8)

            # Объединяем данные и парсим
            data = header + name_data + value_data
            metric = MetricParser.parse(data)
            await store.add(metric)
            logger.debug(f"Received metric: {metric}")
    except (asyncio.IncompleteReadError, ValueError) as e:
        logger.error(f"Error handling client {addr}: {e}")
    finally:
        logger.info(f"Connection closed for {addr}")
        writer.close()
        await writer.wait_closed()

async def start_server(store: MetricStore, host: str, port: int):
    server = await asyncio.start_server(
        lambda r, w: handle_client(r, w, store), host, port
    )
    logger.info(f"Server started on {host}:{port}")
    async with server:
        await server.serve_forever()