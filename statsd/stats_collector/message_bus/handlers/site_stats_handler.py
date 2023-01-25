from datetime import datetime
from http import HTTPStatus
from typing import Optional

from pydantic import BaseModel, HttpUrl, constr

from statsd.stats_collector.message_bus.handlers.base import BaseKafkaHandler
from statsd.stats_collector.postgres import PostgresClient


class SiteStatsSchema(BaseModel):
    url: HttpUrl
    response_code: HTTPStatus
    response_time: float
    started_at: datetime
    regexp_found: Optional[bool]
    regexp: Optional[constr(min_length=1, max_length=255)] = None  # type: ignore


class SiteStatsEventHandler(BaseKafkaHandler):
    topic = "site_stats_events"
    schema = SiteStatsSchema

    @classmethod
    async def handle(cls, message: SiteStatsSchema, database: PostgresClient) -> None:
        query = f"""
            INSERT INTO stats(url, response_code, response_time, started_at, regexp_found, regexp)
            VALUES($1, $2, $3, $4, $5, $6);
        """
        await database.execute(query, *list(message.dict().values()))
