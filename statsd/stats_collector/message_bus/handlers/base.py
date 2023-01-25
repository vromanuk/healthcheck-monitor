from typing import Any, Type

from pydantic import BaseModel

from statsd.stats_collector.postgres import PostgresClient


class BaseKafkaHandler:
    __slots__ = ("topic", "schema")

    topic: str
    schema: Type[BaseModel]

    @classmethod
    async def handle(cls, message: Any, database: PostgresClient) -> None:
        raise NotImplementedError
