import os
import logging
import mcp.server.fastmcp as FastMCP
import httpx

# Configure logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

# Init logger
logger = logging.getLogger(__name__)

# Init MCP server  
mcp = FastMCP(
    name="mcp-gnews-server",
    description="An MCP server for accessing the Google News API.",
)

# Supported languages (GNews API Docs): https://gnews.io/docs/v4#supported-languages
SUPPORTED_LANGUAGES = {
    "ar": "Arabic", "zh": "Chinese", "nl": "Dutch", "en": "English",
    "fr": "French", "de": "German", "el": "Greek", "hi": "Hindi",
    "it": "Italian", "ja": "Japanese", "ml": "Malayalam", "mr": "Marathi",
    "no": "Norwegian", "pt": "Portuguese", "ro": "Romanian", "ru": "Russian",
    "es": "Spanish", "sv": "Swedish", "ta": "Tamil", "te": "Telugu", "uk": "Ukrainian"
}

# Supported countries (GNews API Docs): https://gnews.io/docs/v4#supported-countries
SUPPORTED_COUNTRIES = {
    "au": "Australia", "br": "Brazil", "ca": "Canada", "cn": "China",
    "eg": "Egypt", "fr": "France", "de": "Germany", "gr": "Greece",
    "hk": "Hong Kong", "in": "India", "ie": "Ireland", "it": "Italy",
    "jp": "Japan", "nl": "Netherlands", "no": "Norway", "pk": "Pakistan",
    "pe": "Peru", "ph": "Philippines", "pt": "Portugal", "ro": "Romania",
    "ru": "Russian Federation", "sg": "Singapore", "es": "Spain",
    "se": "Sweden", "ch": "Switzerland", "tw": "Taiwan", "ua": "Ukraine",
    "gb": "United Kingdom", "us": "United States"
}

# GNews API Responde Object: https://docs.gnews.io/json-response
class NewsResponse(BaseModel):
    totalArticles: int
    articles: List[dict]

def main():
    logger.info("Starting MCP GNews Serve")
    mcp.run("stdio")


if __name__ == "__main__":
    main()
