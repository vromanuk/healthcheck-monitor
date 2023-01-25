from pydantic import BaseSettings

from statsd.stats_collector.message_bus import KafkaConfig
from statsd.stats_collector.postgres import PostgresConfig


class Settings(BaseSettings):
    kafka: KafkaConfig
    postgres: PostgresConfig

    class Config:
        env_file = ".env"
        allow_mutation = False
        env_prefix = "APP_"
