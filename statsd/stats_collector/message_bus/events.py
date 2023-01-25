from statsd.stats_collector.message_bus.handlers.site_stats_handler import (
    SiteStatsEventHandler,
)
from statsd.stats_collector.message_bus.registry import EventRegistry

event_registry = EventRegistry()

event_registry.register(SiteStatsEventHandler)
