import os
import pathlib

from pydantic import BaseSettings

from statsd.statsd_exporter.producer import KafkaConfig


class Settings(BaseSettings):
    kafka: KafkaConfig
    basedir: pathlib.Path = pathlib.Path(__file__).parent
    config_path: str = os.path.join(basedir, "config.yaml")

    class Config:
        env_file = ".env"
        allow_mutation = False
        env_prefix = "APP_"
