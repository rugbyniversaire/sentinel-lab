import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "AppleWebKit/537.36 "
        "Chrome/124 Safari/537.36"
    )
}


def _meta(soup, property_name):
    tag = soup.find("meta", property=property_name)

    if tag:
        return tag.get("content")

    tag = soup.find(
        "meta",
        attrs={"name": property_name}
    )

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

    url = resultat.get("lien")

    if not url:
        return resultat

    # on ignore complètement les liens Google News
    if "news.google.com" in url:
        return resultat

    try:

        r = requests.get(
            url,
            headers=HEADERS,
            timeout=8,
            allow_redirects=True,
        )

        soup = BeautifulSoup(
            r.text,
            "html.parser"
        )

        titre = _meta(soup, "og:title")

        if not titre and soup.title:
            titre = soup.title.text.strip()

        # on évite les faux titres
        if titre:

            if titre.lower() not in (
                "google news",
                "google actualités",
            ):

                resultat["titre"] = titre

        description = _meta(
            soup,
            "og:description"
        )

        if description:
            resultat["description"] = description

        image = _meta(
            soup,
            "og:image"
        )

        if image:
            resultat["image"] = image

        media = (
            _meta(soup, "og:site_name")
            or urlparse(url).netloc.replace("www.", "")
        )

        resultat["media"] = media

        resultat["favicon"] = _favicon(
            soup,
            url
        )

    except Exception as e:

        print(e)

    return resultat
