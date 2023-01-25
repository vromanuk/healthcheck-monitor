from unittest.mock import AsyncMock

import pytest

from statsd.statsd_exporter.metrics import MetricsConfig
from statsd.statsd_exporter.settings import Settings


@pytest.fixture
def settings() -> Settings:
    return Settings()


@pytest.fixture
def kafka_producer() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def metrics_config() -> list[MetricsConfig]:
    return [
        MetricsConfig(url="https://python.org"),  # type: ignore
        MetricsConfig(url="https://example.com"),  # type: ignore
    ]
