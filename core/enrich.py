import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse


HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def enrichir_resultat(resultat):
    """
    Enrichit un résultat avec :
    - le vrai lien
    - le vrai titre
    - le média
    - l'image OpenGraph
    - la description
    - le favicon
    """

    url = resultat.get("lien")

    if not url:
        return resultat

    try:

        r = requests.get(
            url,
            timeout=8,
            headers=HEADERS,
            allow_redirects=True,
        )

        url_finale = r.url

        soup = BeautifulSoup(
            r.text,
            "html.parser"
        )

        resultat["lien"] = url_finale

        resultat["titre"] = (
            _meta(soup, "og:title")
            or soup.title.string
            if soup.title
            else resultat["titre"]
        )

        resultat["description"] = (
            _meta(soup, "og:description")
            or ""
        )

        resultat["image"] = (
            _meta(soup, "og:image")
            or resultat.get("image")
        )

        resultat["media"] = (
            _meta(soup, "og:site_name")
            or urlparse(url_finale).netloc
        )

        resultat["favicon"] = (
            _favicon(soup, url_finale)
        )

    except Exception:

        pass

    return resultat


def _meta(soup, prop):

    tag = soup.find(
        "meta",
        property=prop
    )

    if tag:

        return tag.get("content")

    return None


def _favicon(soup, url):

    icon = soup.find(
        "link",
        rel=lambda x: x and "icon" in x.lower()
    )

    if icon:

        href = icon.get("href")

        if href:

            if href.startswith("http"):

                return href

            from urllib.parse import urljoin

            return urljoin(url, href)

    return None
