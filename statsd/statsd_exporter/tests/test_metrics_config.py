from unittest.mock import patch

import pytest

from statsd.statsd_exporter.main import get_metrics_config
from statsd.statsd_exporter.settings import Settings


def test_get_metrics_config(settings: Settings) -> None:
    metrics_config, frequency = get_metrics_config(settings)
    assert metrics_config
    assert frequency


@patch(
    "statsd.statsd_exporter.main.yaml.safe_load",
    return_value={"sites": [], "frequency": -1},
)
def test_get_metrics_config_frequency_validation(settings: Settings) -> None:
    with pytest.raises(ValueError):
        get_metrics_config(settings)
