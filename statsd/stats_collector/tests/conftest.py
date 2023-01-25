import json
from typing import Any, AsyncGenerator, Awaitable, Callable

import pytest
import pytest_asyncio
from asyncpg import Record

from statsd.stats_collector.message_bus import SiteStatsEventHandler
from statsd.stats_collector.postgres import PostgresClient
from statsd.stats_collector.settings import Settings


@pytest.fixture
def settings() -> Settings:
    return Settings()


@pytest_asyncio.fixture
async def postgres_client(settings: Settings) -> AsyncGenerator[PostgresClient, None]:
    client = PostgresClient(settings.postgres)
    await client.startup()
    await client.migrate()
    yield client
    await client.execute("TRUNCATE stats;")
    await client.shutdown()


@pytest_asyncio.fixture(name="handle_kafka_event")
async def _handle_kafka_event(
    postgres_client: PostgresClient,
) -> Callable[..., Awaitable[None]]:
    event_handler = SiteStatsEventHandler()

    async def _handle(
        message: Any,
        repeat: int = 2,
    ) -> None:
        # we are handling event twice because kafka follows `At-Least-Once` Delivery
        # hence we should process duplicate event as normal, without side effects
        for _ in range(repeat):
            await event_handler.handle(
                event_handler.schema(**json.loads(message)), database=postgres_client
            )

    return _handle


@pytest_asyncio.fixture(name="get_metrics")
async def _get_metrics(
    postgres_client: PostgresClient,
) -> Callable[..., Awaitable[list[Record]]]:
    async def _execute(url: str) -> list[Record]:
        return await postgres_client.fetch(
            """
            SELECT * FROM stats
            WHERE url = $1
        """,
            url,
        )

    return _execute
