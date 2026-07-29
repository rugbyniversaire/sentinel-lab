import requests

from core.filters import est_recent
from core.utils import parser_date_iso


def chercher_bluesky(mot_cle, seuil):

    url = (
        "https://public.api.bsky.app/xrpc/"
        "app.bsky.feed.searchPosts"
    )

    params = {

        "q": mot_cle,

        "sort": "latest",

        "limit": 25

    }

    headers = {

        "User-Agent": "sentinel-lab"

    }

    try:

        reponse = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=10
        )

        if reponse.status_code != 200:
            return []

        data = reponse.json()

    except Exception:

        return []

    resultats = []

    for post in data.get("posts", []):

        try:

            record = post.get("record", {})

            date_pub = parser_date_iso(
                record.get("createdAt")
            )

            if not est_recent(date_pub, seuil):
                continue

            auteur = post.get("author", {})

            handle = auteur.get("handle", "")

            uri = post.get("uri", "")

            rkey = uri.split("/")[-1]

            image = None

            embed = post.get("embed", {})

            if embed.get("images"):
                image = embed["images"][0].get("thumb")

            elif embed.get("external", {}).get("thumb"):
                image = embed["external"]["thumb"]

            resultats.append({

                "source": "Bluesky - @" + handle,

                "titre": record.get(
                    "text",
                    ""
                )[:120],

                "lien": (
                    f"https://bsky.app/profile/{handle}/post/{rkey}"
                ),

                "date_pub": date_pub,

                "image": image

            })

        except Exception:
            continue

    return resultats
