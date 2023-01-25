import enum
import logging
from typing import Any

from aiokafka import AIOKafkaConsumer
from pydantic import BaseModel

from statsd.manage_ssl import get_ssl_context

logger = logging.getLogger()


@enum.unique
class KafkaAutoOffsetReset(str, enum.Enum):
    EARLIEST = "earliest"
    LATEST = "latest"


class KafkaConfig(BaseModel):
    servers: list[str]
    auto_offset_reset: KafkaAutoOffsetReset = KafkaAutoOffsetReset.EARLIEST
    enable_auto_commit: bool = True
    auto_commit_interval_ms: int = 1000
    security_protocol: str = "SSL"
    ssl_context: dict[str, Any]


class KafkaClient:
    def __init__(self, config: KafkaConfig) -> None:
        self._config = config
        self._consumer: AIOKafkaConsumer

    async def listen(self, topics: list[str]) -> AIOKafkaConsumer:
        self._consumer = AIOKafkaConsumer(
            bootstrap_servers=self._config.servers,
            group_id="site_stats_events__stats_collector",
            enable_auto_commit=self._config.enable_auto_commit,
            auto_commit_interval_ms=self._config.auto_commit_interval_ms,
            auto_offset_reset=self._config.auto_offset_reset,
            security_protocol=self._config.security_protocol,
            ssl_context=get_ssl_context(self._config.ssl_context),
        )

        await self._consumer.start()
        logger.info("kafka.conn.established")
        self._consumer.subscribe(topics)

        return self._consumer

    async def shutdown(self) -> None:
        await self._consumer.stop()
        logger.info("kafka.conn.closed")
