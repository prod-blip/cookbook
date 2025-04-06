from typing import Any
import httpx
import json
from mcp.server.fastmcp import FastMCP
import os
from dotenv import load_dotenv

load_dotenv()

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")

mcp = FastMCP("linkedin_profile_scraper")


URL = "https://linkedin-api8.p.rapidapi.com/"
RAPIDAPI_HOST = "linkedin-api8.p.rapidapi.com"

async def get_linkedin_data(username: str) -> dict[str, Any] | None:
    
    params = {
        "username": username,
    }
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                URL,
                headers=headers,
                params=params,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
        except Exception:
            print(f"Error fetching LinkedIn data:")
            return None

@mcp.tool()
async def get_profile(username: str) -> str:
    data = await get_linkedin_data(username)
    if not data:
        return "Unable to fetch LinkedIn profile data."
    return json.dumps(data, indent=2)

if __name__ == "__main__":
    mcp.run(transport="stdio")