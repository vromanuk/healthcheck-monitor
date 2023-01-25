from datetime import datetime
from http import HTTPStatus
from typing import Optional

from pydantic import BaseModel, HttpUrl, PositiveInt, constr

from statsd.statsd_exporter.constants import DEFAULT_TIMEOUT


class MetricsConfig(BaseModel):
    url: HttpUrl
    timeout: PositiveInt = DEFAULT_TIMEOUT
    regexp: Optional[constr(min_length=1, max_length=255)]  # type: ignore


class GatheredMetrics(BaseModel):
    url: HttpUrl
    regexp_found: bool
    started_at: datetime
    response_time: float
    response_code: HTTPStatus
    regexp: Optional[constr(min_length=1, max_length=255)]  # type: ignore
