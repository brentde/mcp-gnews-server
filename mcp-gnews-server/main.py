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


def main():
    logger.info("Starting MCP GNews Serve")
    mcp.run("stdio")


if __name__ == "__main__":
    main()
