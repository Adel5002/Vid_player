import asyncio
import json

import requests

from kodik_api_calls.kodik_settings import KODIK_TOKEN, KODIK_SEARCH


async def get_player_by_anime_name(anime_name: str) -> str:
    params = {
        "token": KODIK_TOKEN,
        "title": anime_name
    }
    kodik_api_url = requests.get(KODIK_SEARCH, params=params)
    try:
        result = kodik_api_url.json()["results"]
        return result
    except Exception:
        print("Такого аниме в кодик еще нет 🔒")
        return "none"

if __name__ == "__main__":
    print(json.dumps(asyncio.run(get_player_by_anime_name('наруто')), indent=4))