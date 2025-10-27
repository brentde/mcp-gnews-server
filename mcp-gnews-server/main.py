import os
import logging
from typing import Optional, Literal, List
from datetime import datetime
from enum import Enum

import httpx
from pydantic import BaseModel, Field, validator
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()

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
    instructions="An MCP server for accessing the Google News API.",
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

# GNews API Response Object: https://docs.gnews.io/json-response
class NewsResponse(BaseModel):
    totalArticles: int
    articles: List[dict]

def get_api_key() -> str:
    api_key = os.getenv("GNEWS_API_KEY")
    if not api_key:
        raise ValueError("Missing GNEWS_API_KEY environment variable.")
    return api_key


# Get the api key
# Formulate the request to GNews API
# Get HTTPx client
# Execute the request
async def make_gnews_request(endpoint: str, params: dict) -> dict:
    api_key = get_api_key()    
    # Add API key to parameters
    params["apikey"] = api_key
    # Base URL for GNews API
    base_url = "https://gnews.io/api/v4"
    url = f"{base_url}/{endpoint}"
    
    try:
        async with httpx.AsyncClient() as client:
            logger.info(f"Making request to {endpoint} with params: {params}")
            response = await client.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Successfully retrieved {data.get('totalArticles', 0)} articles")
                return data
            else:
                error_msg = f"GNews API error: {response.status_code}"
                try:
                    error_data = response.json()
                    if "errors" in error_data:
                        error_msg += f" - {error_data['errors']}"
                except:
                    error_msg += f" - {response.text}"
                
                logger.error(error_msg)
                raise Exception(error_msg)
                
    except httpx.RequestError as e:
        error_msg = f"Network error connecting to GNews API: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)


@mcp.tool()
async def search_news(
    q: str = Field(description="Search keywords. Use logical operators like AND, OR, NOT. Use quotes for exact phrases."),
    lang: Optional[str] = Field(default=None, description=f"Language code (2 letters). Supported: {', '.join(SUPPORTED_LANGUAGES.keys())}"),
    country: Optional[str] = Field(default=None, description=f"Country code (2 letters). Supported: {', '.join(SUPPORTED_COUNTRIES.keys())}"),
    max_articles: Optional[int] = Field(default=10, description="Number of articles to return (1-100)"),
    search_in: Optional[str] = Field(default=None, description="Search in specific fields: title, description, content (comma-separated)"),
    nullable: Optional[str] = Field(default=None, description="Allow null values for: description, content, image (comma-separated)"),
    date_from: Optional[str] = Field(default=None, description="Filter articles from this date (ISO 8601 format: YYYY-MM-DDTHH:MM:SS.sssZ)"),
    date_to: Optional[str] = Field(default=None, description="Filter articles until this date (ISO 8601 format: YYYY-MM-DDTHH:MM:SS.sssZ)"),
    sortby: Optional[Literal["publishedAt", "relevance"]] = Field(default="publishedAt", description="Sort by publication date or relevance"),
    page: Optional[int] = Field(default=1, description="Page number for pagination")
) -> dict:    
    
    # Build request parameters
    params = { "q": q }
    
    if lang:
        params["lang"] = lang
    if country:
        params["country"] = country
    if max_articles:
        params["max"] = max_articles
    if search_in:
        params["in"] = search_in
    if nullable:
        params["nullable"] = nullable
    if date_from:
        params["from"] = date_from
    if date_to:
        params["to"] = date_to
    if sortby:
        params["sortby"] = sortby
    if page:
        params["page"] = page
    
    try:
        result = await make_gnews_request("search", params)
        return {
            "success": True,
            "query": q,
            "totalArticles": result.get("totalArticles", 0),
            "articles": result.get("articles", []),
            "parameters_used": params
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "query": q,
            "parameters_used": params
        }

def main():
    logger.info("Starting MCP GNews Serve")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
