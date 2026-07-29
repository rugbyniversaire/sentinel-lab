import requests

from datetime import datetime, timezone


def chercher_hackernews(mot_cle, seuil):

    url = "https://hn.algolia.com/api/v1/search_by_date"

    params = {

        "query": mot_cle,

        "tags": "story",

        "numericFilters": (
            f"created_at_i>{int(seuil.timestamp())}"
        )

    }

    try:

        reponse = requests.get(
            url,
            params=params,
            timeout=10
        )

        data = reponse.json()

        resultats = []

        for hit in data.get("hits", []):

            resultats.append({

                "source": "Hacker News",

                "titre": hit.get("title", ""),

                "lien": hit.get("url")
                or f"https://news.ycombinator.com/item?id={hit.get('objectID')}",

                "date_pub": datetime.fromtimestamp(
                    hit.get("created_at_i", 0),
                    tz=timezone.utc
                ),

                "image": None

            })

        return resultats

    except Exception:

        return []
