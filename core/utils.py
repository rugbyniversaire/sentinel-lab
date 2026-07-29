import re

from datetime import datetime


def parser_date_iso(chaine):

    if not chaine:
        return None

    chaine = chaine.replace(
        "Z",
        "+00:00"
    )

    match = re.match(
        r"^(.*?\.\d{1,6})\d*(\+.*)$",
        chaine
    )

    if match:
        chaine = match.group(1) + match.group(2)

    try:
        return datetime.fromisoformat(chaine)

    except ValueError:
        return None


def extraire_image_html(html):

    if not html:
        return None

    match = re.search(
        r'<img[^>]+src="([^"]+)"',
        html
    )

    if match:
        return match.group(1)

    return None
