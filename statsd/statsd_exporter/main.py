import asyncio
import datetime
import logging
import signal
import time
from typing import Any

import yaml
from aiohttp import ClientSession

from statsd.logger import configure_logging
from statsd.statsd_exporter.http_client import HTTPClient
from statsd.statsd_exporter.metrics import GatheredMetrics, MetricsConfig
from statsd.statsd_exporter.producer import KafkaProducer
from statsd.statsd_exporter.settings import Settings

logger = logging.getLogger()


async def main(producer: KafkaProducer) -> None:
    configure_logging()

    await producer.startup()

    logger.info(f"loading config from yaml {settings.config_path}")
    metrics_config, frequency = get_metrics_config(settings)

    shutdown = False

    async def signal_handler(sig: Any) -> None:
        logger.info(f"received exit signal {sig.name}...")
        nonlocal shutdown
        shutdown = True

    loop = asyncio.get_event_loop()
    signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
    for s in signals:
        loop.add_signal_handler(s, lambda s=s: asyncio.create_task(signal_handler(s)))

    try:
        while not shutdown:
            asyncio.create_task(
                gather_metrics(producer=producer, metrics_config=metrics_config)
            )
            await asyncio.sleep(frequency)
    finally:
        await producer.shutdown()


def get_metrics_config(settings: Settings) -> tuple[list[MetricsConfig], int]:
    with open(settings.config_path, "r") as c:
        config = yaml.safe_load(c)
    metrics_config = [
        MetricsConfig(url=mc["url"], timeout=mc["timeout"], regexp=mc["regexp"])
        for mc in config["sites"]
    ]
    frequency = config["frequency"]
    if frequency < 0:
        raise ValueError("frequency cannot be less than 0")
    return metrics_config, frequency


async def gather_metrics(
    producer: KafkaProducer, metrics_config: list[MetricsConfig]
) -> None:
    logger.info(f"gathering metrics process started")
    async with ClientSession() as client:
        http_client = HTTPClient(session=client)
        tasks = [
            asyncio.create_task(gather_site_metrics(http_client, c))
            for c in metrics_config
        ]
        metrics = await asyncio.gather(*tasks)

    logger.info(f"metrics have been gathered")

    await produce_events(producer=producer, metrics=metrics)


async def gather_site_metrics(
    client: HTTPClient, config: MetricsConfig
) -> GatheredMetrics:
    start = time.perf_counter()
    response = await client.get(
        request_url=config.url, regexp=config.regexp, timeout=config.timeout
    )
    elapsed_time = time.perf_counter() - start

    return GatheredMetrics(
        url=config.url,
        response_code=response.response_code,  # type: ignore
        regexp_found=response.regexp_found,
        regexp=response.regexp,
        started_at=datetime.datetime.utcnow(),
        response_time=elapsed_time,
    )


async def produce_events(
    producer: KafkaProducer, metrics: list[GatheredMetrics]
) -> None:
    for metric in metrics:
        try:
            await producer.enqueue(metric.json())
        except Exception as e:
            logger.error(e)

    logger.info(f"metrics have been enqueued")


if __name__ == "__main__":
    settings = Settings()
    kafka_producer = KafkaProducer(settings.kafka, topic="site_stats_events")
    asyncio.run(main(producer=kafka_producer))
