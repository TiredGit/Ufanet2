import logging
from aiokafka import AIOKafkaConsumer
import asyncio
import json
from storage import add_event
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def consume():
    """
        Асинхронный Kafka consumer.

        Подключается к брокеру Kafka, слушает события с топиков WAL-репликации
        (`wal_listener.wal_city`, `wal_listener.wal_company`, и др.) и передаёт
        полученные сообщения в функцию `add_event()`.

        Перед запуском ожидает задержку в секундах из переменной окружения
        `KAFKA_STARTUP_DELAY` (по умолчанию — 10 секунд).
    """
    delay = int(os.getenv("KAFKA_STARTUP_DELAY", "10"))
    await asyncio.sleep(delay)
    consumer = AIOKafkaConsumer(
        "wal_listener.wal_city",
        "wal_listener.wal_company",
        "wal_listener.wal_discount",
        "wal_listener.wal_category",
        #bootstrap_servers="localhost:9093",
        bootstrap_servers="kafka:9092",
        group_id=None,
        auto_offset_reset="earliest",
        value_deserializer=lambda m: json.loads(m.decode("utf-8"))
    )
    await consumer.start()
    logger.info("Kafka consumer started")
    try:
        async for msg in consumer:
            logger.info(f"Received message: {msg.value}")
            add_event(msg.value)
    except Exception as e:
        logger.error(f"Error in consumer: {e}")
    finally:
        await consumer.stop()
        logger.info("Kafka consumer stopped")
