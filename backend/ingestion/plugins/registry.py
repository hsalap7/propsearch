from typing import Type
from ingestion.plugins.base import SourcePlugin
from ingestion.plugins.mock import MockPlugin
from ingestion.plugins.connectors import JSONPlugin, CSVPlugin, ExcelPlugin, BuilderWebsitePlugin, ManualUploadPlugin

# Dynamically mapped source plugins
SOURCES: dict[str, Type[SourcePlugin]] = {
    "mock_source": MockPlugin,
    "json_upload": JSONPlugin,
    "csv_upload": CSVPlugin,
    "excel_upload": ExcelPlugin,
    "builder_direct": BuilderWebsitePlugin,
    "manual_upload": ManualUploadPlugin,
}
