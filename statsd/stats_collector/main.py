import asyncio
import json
import logging
import signal
from typing import Any

from statsd.logger import configure_logging
from statsd.stats_collector.message_bus import KafkaClient, event_registry
from statsd.stats_collector.postgres import PostgresClient
from statsd.stats_collector.settings import Settings

logger = logging.getLogger()


async def main(kafka_client: KafkaClient, database: PostgresClient) -> None:
    configure_logging()
    loop = asyncio.get_event_loop()
    signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
    for s in signals:
        loop.add_signal_handler(s, lambda s=s: asyncio.create_task(shutdown(s, loop)))

    try:
        await init_db(database)
        await consume(kafka_client, database)
    except asyncio.CancelledError:
        for i in range(3):
            await asyncio.sleep(1)
    finally:
        await database.shutdown()
        await kafka_client.shutdown()


async def shutdown(sig: Any, loop: asyncio.AbstractEventLoop) -> None:
    logger.info(f"Received exit signal {sig.name}...")
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    [task.cancel() for task in tasks]
    logger.info(f"Cancelling {len(tasks)} tasks")
    await asyncio.gather(*tasks, return_exceptions=True)

    loop.stop()


async def consume(kafka_client: KafkaClient, database: PostgresClient) -> None:
    consumer = await kafka_client.listen(topics=event_registry.topics)

    try:
        async for message in consumer:
            logger.info(f"consuming message from {message.topic}")
            handler = event_registry.topic_dispatcher[message.topic]
            await handler.handle(
                message=handler.schema(**json.loads(message.value)), database=database
            )
    except Exception as e:
        logger.error(e)


async def init_db(database: PostgresClient) -> None:
    await database.startup()
    await database.migrate()


if __name__ == "__main__":
    settings = Settings()
    kafka = KafkaClient(settings.kafka)
    db = PostgresClient(settings.postgres)
    asyncio.run(main(kafka_client=kafka, database=db))
