import logging
from typing import Any

from aiokafka import AIOKafkaProducer
from pydantic import BaseModel

from statsd.manage_ssl import get_ssl_context

logger = logging.getLogger()


class KafkaConfig(BaseModel):
    servers: list[str]
    security_protocol: str = "SSL"
    ssl_context: dict[str, Any]


class KafkaProducer:
    def __init__(self, config: KafkaConfig, topic: str):
        self._config = config
        self.topic = topic
        self._producer: AIOKafkaProducer

    async def startup(self) -> None:
        self._producer = AIOKafkaProducer(
            bootstrap_servers=self._config.servers,
            security_protocol=self._config.security_protocol,
            ssl_context=get_ssl_context(self._config.ssl_context),
        )
        await self._producer.start()
        logger.info("kafka.producer.conn.established")

    async def shutdown(self) -> None:
        await self._producer.stop()

        logger.info("kafka.producer.conn.closed")

    async def enqueue(self, message: str) -> None:
        await self._producer.send(topic=self.topic, value=message.encode())
        logger.info(f"message: {message} enqueued")
