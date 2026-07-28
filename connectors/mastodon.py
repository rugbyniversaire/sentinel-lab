import requests

from core.filters import est_recent
from core.utils import parser_date_iso


def chercher_mastodon(mot_cle, seuil):
    url = "https://mastodon.social/api/v2/search"

    params = {
        "q": mot_cle,
        "type": "statuses",
        "limit": 25,
    }

    headers = {
        "User-Agent": "veille-outil/1.0"
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

        resultats = []

        for statut in data.get("statuses", []):

            date_pub = parser_date_iso(statut.get("created_at"))

            if est_recent(date_pub, seuil):

                pieces_jointes = statut.get("media_attachments", [])

                image = (
                    pieces_jointes[0].get("preview_url")
                    if pieces_jointes
                    else None
                )

                resultats.append({
                    "source": "Mastodon - @" + statut.get("account", {}).get("acct", ""),
                    "titre": statut.get("content", "")[:120],
                    "lien": statut.get("url", ""),
                    "date_pub": date_pub,
                    "image": image
                })

        return resultats

    except Exception:
        return []
