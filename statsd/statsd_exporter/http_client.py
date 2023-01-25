import logging
from http import HTTPStatus
from typing import Optional

from aiohttp import ClientSession, ClientTimeout
from pydantic import BaseModel

from statsd.statsd_exporter.constants import DEFAULT_TIMEOUT

logger = logging.getLogger()


class Response(BaseModel):
    response_code: int
    regexp_found: bool = False
    regexp: Optional[str]


class HTTPClient:
    def __init__(self, session: ClientSession):
        self._session = session

    async def get(
        self,
        request_url: str,
        timeout: int = DEFAULT_TIMEOUT,
        regexp: Optional[str] = None,
    ) -> Response:
        return await self.__make_http_request(
            method="GET", request_url=request_url, timeout=timeout, regexp=regexp
        )

    async def __make_http_request(
        self,
        method: str,
        request_url: str,
        timeout: int = DEFAULT_TIMEOUT,
        regexp: Optional[str] = None,
    ) -> Response:
        session_timeout = ClientTimeout(total=timeout)

        logger.info(
            f"requesting metrics for `{request_url}` with timeout={session_timeout.total}"
        )

        async with self._session.request(
            method=method,
            url=request_url,
            timeout=timeout,
        ) as response:
            regexp_found = False
            if regexp and response.status == HTTPStatus.OK:
                body = await response.text()
                regexp_found = True if regexp in body else False

            return Response(
                response_code=response.status, regexp_found=regexp_found, regexp=regexp
            )
