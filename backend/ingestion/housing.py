from ingestion.portal import PortalCollector


class HousingCollector(PortalCollector):
    source = "housing"
    requests_per_minute = 30
    listing_url_pattern = r"housing\.com/in/buy/resale/page/"
    search_urls: list[str] = [
        "https://housing.com/in/buy/real-estate-bangalore",
    ]


HousingComSource = HousingCollector
