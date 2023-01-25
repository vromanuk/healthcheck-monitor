import datetime
from http import HTTPStatus
from typing import Any, Awaitable, Callable

import pytest
from asyncpg import Record

from statsd.stats_collector.message_bus import SiteStatsSchema

pytestmark = pytest.mark.asyncio


async def test_consume_event(
    handle_kafka_event: Callable[..., Awaitable[None]],
    get_metrics: Callable[..., Awaitable[list[Record]]],
) -> None:
    url = "https://python.org"

    assert not await get_metrics(url)

    message = SiteStatsSchema(
        url=url,  # type: ignore
        response_code=HTTPStatus.OK,
        response_time=1.13,
        started_at=datetime.datetime.utcnow(),
        regexp_found=False,
    )
    await handle_kafka_event(message.json())

    metrics = await get_metrics(url)
    assert metrics
    assert all(url in metric["url"] for metric in metrics)
