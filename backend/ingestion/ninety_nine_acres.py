from ingestion.portal import PortalCollector


class NinetyNineAcresCollector(PortalCollector):
    source = "99acres"
    requests_per_minute = 20
    listing_url_pattern = r"99acres\.com/.+"
    search_urls: list[str] = []
