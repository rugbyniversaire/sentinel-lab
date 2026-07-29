from datetime import (
    datetime,
    timezone,
    timedelta
)

from core.constants import LIMITE_HEURES

from core.filters import (
    est_pertinent,
    dedupliquer
)

from connectors.google_news import chercher_google_news
from connectors.reddit import chercher_reddit
from connectors.hackernews import chercher_hackernews
from connectors.mastodon import chercher_mastodon
from connectors.bluesky import chercher_bluesky
from connectors.youtube import chercher_youtube


def rechercher_tout(mot_cle):

    maintenant = datetime.now(
        timezone.utc
    )

    seuil = maintenant - timedelta(
        hours=LIMITE_HEURES
    )

    resultats = (

        chercher_google_news(
            mot_cle,
            seuil
        )

        + chercher_reddit(
            mot_cle,
            seuil
        )

        + chercher_hackernews(
            mot_cle,
            seuil
        )

        + chercher_mastodon(
            mot_cle,
            seuil
        )

        + chercher_bluesky(
            mot_cle,
            seuil
        )

        + chercher_youtube(
            mot_cle,
            seuil
        )

    )

    resultats = [

        r

        for r in resultats

        if est_pertinent(
            mot_cle,
            r["titre"]
        )

    ]

    resultats = dedupliquer(
        resultats
    )

    resultats.sort(

        key=lambda r: r["date_pub"],

        reverse=True

    )

    return resultats, maintenant
