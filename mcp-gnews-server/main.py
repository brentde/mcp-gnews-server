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

async def configure_gnews_request(endpoint: str, params: dict) -> dict:
    url = f"https://gnews.io/api/v4/{endpoint}"
    api_key = get_api_key()    
    params["apikey"] = api_key
    
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
                logger.error(error_msg)
                raise Exception(error_msg)
                
    except httpx.RequestError as e:
        error_msg = f"Network error connecting to GNews API: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)


def main():
    logger.info("Starting MCP GNews Serve")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
