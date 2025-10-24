import os
import asyncio
import time
from datetime import date
from typing import List, Dict, Optional, Union

from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
from gql.transport.exceptions import TransportQueryError, TransportServerError
from dotenv import load_dotenv

load_dotenv()

# ✅ создаем транспорт и клиент один раз
_TRANSPORT = AIOHTTPTransport(
    url=os.getenv("SHIKIMORI_GRAPHQL"),
    timeout=30  # увеличенный таймаут
)

_CLIENT = Client(
    transport=_TRANSPORT,
    fetch_schema_from_transport=False,
    execute_timeout=30
)

# =============================
# 🔹 Универсальная функция выполнения GraphQL-запроса
# =============================

async def _execute_graphql_query(
    query: str,
    variables: dict,
    retries: int = 3,
    delay: float = 2.0,
) -> Optional[dict]:
    for attempt in range(1, retries + 1):
        try:
            start = time.monotonic()

            # ✅ создаём отдельный клиент для каждого вызова (безопасно)
            async with Client(
                transport=_TRANSPORT,
                fetch_schema_from_transport=False,
                execute_timeout=30,
            ) as session:
                result = await session.execute(gql(query), variable_values=variables)

            took = time.monotonic() - start
            if took > 2:
                print(f"⏱ GraphQL запрос ({variables}) занял {took:.2f}s")
            return result

        except asyncio.TimeoutError:
            print(f"⚠️ Timeout (попытка {attempt}/{retries}) — {variables}")
        except (TransportQueryError, TransportServerError) as e:
            print(f"⚠️ GraphQL транспортная ошибка: {e}")
        except Exception as e:
            print(f"❌ Неожиданная ошибка GraphQL (попытка {attempt}/{retries}): {e}")

        await asyncio.sleep(delay * attempt)

    print(f"❌ Запрос GraphQL не удался после {retries} попыток: {variables}")
    return None



# =============================
# 🔸 Запрос списка аниме (по сезону, статусу и странице)
# =============================

_ANIME_LIST_QUERY = """
query getAnimeList ($limit: Int!, $season: SeasonString!, $status: AnimeStatusString!, $page: Int!) {
  animes(limit: $limit, order: popularity, season: $season, status: $status, page: $page) {
    id
    malId
    name
    russian
    licenseNameRu
    english
    japanese
    synonyms
    kind
    rating
    score
    status
    episodes
    episodesAired
    duration
    airedOn { year month day date }
    releasedOn { year month day date }
    url
    season
    poster { id originalUrl main2xUrl }
    fansubbers
    fandubbers
    licensors
    createdAt
    updatedAt
    nextEpisodeAt
    isCensored
    genres { id name russian kind }
    studios { id name imageUrl }
    videos { id url name kind playerUrl imageUrl }
    screenshots { id originalUrl }
    description
    descriptionHtml
    descriptionSource
  }
}
"""


async def get_anime_list(
    limit: int = 50,
    season: str = f"{date.today().year}",
    status: str = "",
    page: int = 1,
):
    variables = {
        "limit": limit,
        "season": season,
        "status": status,
        "page": page,
    }
    result = await _execute_graphql_query(_ANIME_LIST_QUERY, variables)
    return result


# =============================
# 🔸 Поиск аниме по имени или ID
# =============================

_SEARCH_ANIME_QUERY = """
query getAnimeList ($ids: String!, $anime_name: String!, $limit: Int!) {
  animes(ids: $ids, search: $anime_name, limit: $limit) {
    id
    malId
    name
    russian
    licenseNameRu
    english
    japanese
    synonyms
    kind
    rating
    score
    status
    episodes
    episodesAired
    duration
    airedOn { year month day date }
    releasedOn { year month day date }
    url
    season
    poster { id originalUrl main2xUrl }
    fansubbers
    fandubbers
    licensors
    createdAt
    updatedAt
    nextEpisodeAt
    isCensored
    genres { id name russian kind }
    studios { id name imageUrl }
    videos { id url name kind playerUrl imageUrl }
    screenshots { id originalUrl }
    description
    descriptionHtml
    descriptionSource
  }
}
"""


async def search_for_anime(
    anime_id: str = "",
    anime_name: str = "",
    limit: int = 50,
) -> List[Dict]:
    variables = {
        "ids": anime_id,
        "anime_name": anime_name,
        "limit": limit,
    }
    result = await _execute_graphql_query(_SEARCH_ANIME_QUERY, variables)
    return result.get("animes") if result else []


if __name__ == "__main__":
    data = asyncio.run(get_anime_list(limit=1))
    print(data["animes"])
