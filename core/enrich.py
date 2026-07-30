import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    )
}


def _meta(soup, property_name):
    tag = soup.find("meta", property=property_name)
    if tag:
        return tag.get("content")

    tag = soup.find("meta", attrs={"name": property_name})
    if tag:
        return tag.get("content")

    return None


def _favicon(soup, url):
    icon = soup.find(
        "link",
        rel=lambda x: x and "icon" in x.lower()
    )

    if icon and icon.get("href"):

        href = icon["href"]

        if href.startswith("http"):
            return href

        return urljoin(url, href)

    parsed = urlparse(url)

    return f"{parsed.scheme}://{parsed.netloc}/favicon.ico"


def enrichir_resultat(resultat):
    """
    Enrichit automatiquement un résultat.
    """

    url = resultat.get("lien")

    if not url:
        return resultat

    try:

        r = requests.get(
            url,
            headers=HEADERS,
            timeout=8,
            allow_redirects=True,
        )

        url_finale = r.url

        soup = BeautifulSoup(
            r.text,
            "html.parser"
        )

        resultat["lien"] = url_finale

        titre = _meta(soup, "og:title")
        if not titre and soup.title:
            titre = soup.title.text.strip()

        if titre:
            resultat["titre"] = titre

        description = _meta(soup, "og:description")
        if description:
            resultat["description"] = description

        image = _meta(soup, "og:image")
        if image:
            resultat["image"] = image

        media = (
            _meta(soup, "og:site_name")
            or urlparse(url_finale).netloc.replace("www.", "")
        )

        resultat["media"] = media

        resultat["favicon"] = _favicon(
            soup,
            url_finale
        )

    except Exception:
        pass

    return resultat
