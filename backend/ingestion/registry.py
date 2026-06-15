import json

from app.core.config import settings
from ingestion.housing import HousingCollector
from ingestion.magicbricks import MagicBricksCollector
from ingestion.ninety_nine_acres import NinetyNineAcresCollector
from ingestion.nobroker import NoBrokerCollector

COLLECTORS = {
    "housing": HousingCollector,
    "magicbricks": MagicBricksCollector,
    "nobroker": NoBrokerCollector,
    "99acres": NinetyNineAcresCollector,
}


def configure_search_urls() -> None:
    """Apply search URLs from a JSON object without coupling core code to sources."""
    if not settings.collector_search_urls:
        return
    configured = json.loads(settings.collector_search_urls)
    for source, urls in configured.items():
        if source in COLLECTORS:
            COLLECTORS[source].search_urls = urls


configure_search_urls()
