from http import HTTPStatus
from unittest.mock import AsyncMock, patch

import pytest

from statsd.statsd_exporter.http_client import Response
from statsd.statsd_exporter.main import gather_metrics
from statsd.statsd_exporter.metrics import MetricsConfig

pytestmark = pytest.mark.asyncio


@patch(
    "statsd.statsd_exporter.main.HTTPClient.get",
    return_value=Response(response_code=HTTPStatus.OK, regexp=None),
)
async def test_gather_metrics(
    kafka_producer: AsyncMock,
    metrics_config: list[MetricsConfig],
) -> None:
    await gather_metrics(
        producer=kafka_producer,
        metrics_config=metrics_config,
    )
    kafka_producer.enqueue.assert_called()
    expected_urls = sorted([m.url for m in metrics_config])
    actual_urls = sorted(
        [call.kwargs["request_url"] for call in kafka_producer.call_args_list]
    )
    assert kafka_producer.call_count == len(metrics_config)
    assert len(expected_urls) == len(actual_urls)
    assert actual_urls == expected_urls
