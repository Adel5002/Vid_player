import asyncio
import os

import requests
from dotenv import load_dotenv

load_dotenv()

KODIK_SEARCH = os.getenv("SEARCH_FOR_SERIAL")
KODIK_TOKEN = os.getenv("KODIK_API_KEY")

async def get_player_by_id(shikimori_id: str) -> str:
    params = {
        "token": KODIK_TOKEN,
        "shikimori_id": shikimori_id
    }
    kodik_api_url = requests.get(KODIK_SEARCH, params=params)
    try:
        result = kodik_api_url.json()["results"][0]["link"]
        return result
    except Exception:
        print("Такого аниме в кодик еще нет 🔒")
        return "none"



if __name__ == "__main__":
    print(asyncio.run(get_player_by_id("59435")))