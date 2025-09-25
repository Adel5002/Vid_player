import asyncio
import json
import os
from datetime import date

from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport

from dotenv import load_dotenv

load_dotenv()



async def get_anime_list(limit: int = 50, season: str = f'{date.today().year}', status: str = '', page: int = 1):
    client = Client(transport=AIOHTTPTransport(os.getenv("SHIKIMORI_GRAPHQL")))

    query = gql(
        """
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

            poster { id originalUrl mainUrl }

            fansubbers
            fandubbers
            licensors
            createdAt,
            updatedAt,
            nextEpisodeAt,
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
    )

    variables = {"limit": limit, "season": season, "status": status, "page": page}

    async with client as session:
        result = await session.execute(query, variable_values=variables)
        return result["animes"]

if __name__ == "__main__":
    data = asyncio.run(get_anime_list(limit=50, page=2))
    print(json.dumps(data, indent=4))
