import logging
from contextlib import asynccontextmanager
from typing import Any, Optional

from asyncpg import Connection, Pool, Record, create_pool

from statsd.stats_collector.postgres.constants import DEFAULT_TIMEOUT
from statsd.stats_collector.postgres.settings import PostgresConfig

logger = logging.getLogger()


class PostgresClient:
    def __init__(self, config: PostgresConfig) -> None:
        self._config = config
        self._pool: Pool

    async def startup(self) -> None:
        self._pool = await create_pool(
            host=self._config.host,
            port=self._config.port,
            database=self._config.database,
            user=self._config.user,
            password=self._config.password,
        )
        logger.info("postgres.conn.established")

    async def shutdown(self) -> None:
        await self._pool.close()
        logger.info("postgres.conn.closed")

    @asynccontextmanager
    async def _acquire(
        self, conn: Optional[Connection] = None, timeout: int = DEFAULT_TIMEOUT
    ) -> Connection:
        if conn:
            yield conn
            return

        async with self._pool.acquire(timeout=timeout) as conn:
            yield conn

    async def execute(
        self,
        query: str,
        *args: Any,
        conn: Optional[Connection] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        async with self._acquire(conn=conn, timeout=timeout) as conn:
            await conn.execute(query, *args)

    async def migrate(self) -> None:
        await self.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')
        await self.execute(
            """
                CREATE TABLE IF NOT EXISTS stats(
                    uuid UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    url VARCHAR(255) NOT NULL,
                    response_code INT NOT NULL,
                    response_time REAL NOT NULL,
                    started_at TIMESTAMP NOT NULL,
                    regexp_found BOOL,
                    regexp VARCHAR(255)
                )
            """
        )
        await self.execute(
            """
            CREATE INDEX CONCURRENTLY
            IF NOT EXISTS ix_stats_url
            ON stats (url)
        """
        )

    async def fetch(
        self,
        query: str,
        *args: Any,
        conn: Optional[Connection] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> list[Record]:
        async with self._acquire(conn=conn, timeout=timeout) as conn:
            return await conn.fetch(query, *args)
