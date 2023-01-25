from dataclasses import dataclass, field
from typing import Type

from statsd.stats_collector.message_bus.handlers.base import BaseKafkaHandler


@dataclass(frozen=True)
class EventRegistry:
    topic_dispatcher: dict[str, Type[BaseKafkaHandler]] = field(default_factory=dict)

    def register(self, handler: Type[BaseKafkaHandler]) -> None:
        self.topic_dispatcher[handler.topic] = handler

    @property
    def topics(self) -> list[str]:
        return list(self.topic_dispatcher.keys())
