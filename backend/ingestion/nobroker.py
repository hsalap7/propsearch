from ingestion.portal import PortalCollector


class NoBrokerCollector(PortalCollector):
    source = "nobroker"
    requests_per_minute = 20
    listing_url_pattern = r"nobroker\.in/property/"
    search_urls: list[str] = []


NoBrokerSource = NoBrokerCollector
