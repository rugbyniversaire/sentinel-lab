import feedparser

from datetime import datetime, timezone
from urllib.parse import quote

from core.filters import est_recent
from core.utils import extraire_image_html


def chercher_google_news(mot_cle, seuil):

    url = (
        "https://news.google.com/rss/search"
        f"?q={quote(mot_cle)}&hl=fr&gl=FR&ceid=FR:fr"
    )

    flux = feedparser.parse(url)

    resultats = []

    for entree in flux.entries:

        date_pub = None

        if entree.get("published_parsed"):

            date_pub = datetime(
                *entree.published_parsed[:6],
                tzinfo=timezone.utc
            )

        if not est_recent(date_pub, seuil):
            continue

        titre = entree.title

        media = None

        if " - " in titre:

            titre_sans_media, _, media = titre.rpartition(" - ")

            if titre_sans_media.strip():
                titre = titre_sans_media.strip()

        image = extraire_image_html(
            entree.get("summary", "")
        )

        resultats.append({

            "source": "Google News" + (
                f" - {media.strip()}" if media else ""
            ),

            "titre": titre,

            "lien": entree.link,

            "date_pub": date_pub,

            "image": image

        })

    return resultats
