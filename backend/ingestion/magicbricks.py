from ingestion.portal import PortalCollector


class MagicBricksCollector(PortalCollector):
    source = "magicbricks"
    requests_per_minute = 30
    listing_url_pattern = r"magicbricks\.com/propertyDetails/"
    search_urls: list[str] = []


MagicBricksSource = MagicBricksCollector
