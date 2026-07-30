import requests
from bs4 import BeautifulSoup


CACHE_IMAGES = {}


def recuperer_image_article(url):
    """
    Récupère automatiquement l'image principale d'un article
    via la balise OpenGraph.
    """

    if not url:
        return None

    if url in CACHE_IMAGES:
        return CACHE_IMAGES[url]

    try:

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        r = requests.get(
            url,
            timeout=6,
            headers=headers
        )

        soup = BeautifulSoup(r.text, "html.parser")

        balise = soup.find(
            "meta",
            property="og:image"
        )

        if balise:

            image = balise.get("content")

            CACHE_IMAGES[url] = image

            return image

    except Exception:

        pass

    CACHE_IMAGES[url] = None

    return None
