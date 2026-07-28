import feedparser

from datetime import datetime, timezone
from urllib.parse import quote

from core.filters import est_recent
from core.utils import extraire_image_html


def chercher_google_news(mot_cle, seuil):
    url = f"https://news.google.com/rss/search?q={quote(mot_cle)}&hl=fr&gl=FR&ceid=FR:fr"

    flux = feedparser.parse(url)

    resultats = []

    for entree in flux.entries:

        date_pub = None

        if entree.get("published_parsed"):
            date_pub = datetime(*entree.published_parsed[:6], tzinfo=timezone.utc)

        if not est_recent(date_pub, seuil):
            continue

        titre_brut = entree.title

        media = None

        if " - " in titre_brut:
            titre_sans_media, _, media = titre_brut.rpartition(" - ")

            if titre_sans_media.strip():
                titre_brut = titre_sans_media.strip()

        source_label = "Google News"

        if media:
            source_label += f" - {media.strip()}"

        image = extraire_image_html(entree.get("summary", ""))

        resultats.append({
            "source": source_label,
            "titre": titre_brut,
            "lien": entree.link,
            "date_pub": date_pub,
            "image": image
        })

    return resultats
