from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone, timedelta

from core.constants import LIMITE_HEURES
from core.filters import est_pertinent, dedupliquer

from connectors.google_news import chercher_google_news
from connectors.reddit import chercher_reddit
from connectors.hackernews import chercher_hackernews
from connectors.mastodon import chercher_mastodon
from connectors.bluesky import chercher_bluesky
from connectors.youtube import chercher_youtube


def rechercher_tout(mot_cle):
    """
    Recherche un seul mot-clé sur toutes les sources.
    """

    maintenant = datetime.now(timezone.utc)
    seuil = maintenant - timedelta(hours=LIMITE_HEURES)

    tous = (
        chercher_google_news(mot_cle, seuil)
        + chercher_reddit(mot_cle, seuil)
        + chercher_hackernews(mot_cle, seuil)
        + chercher_mastodon(mot_cle, seuil)
        + chercher_bluesky(mot_cle, seuil)
        + chercher_youtube(mot_cle, seuil)
    )

    tous = [
        r
        for r in tous
        if est_pertinent(mot_cle, r["titre"])
    ]

    tous = dedupliquer(tous)

    tous.sort(
        key=lambda r: r["date_pub"],
        reverse=True
    )

    return tous, maintenant


def rechercher_plusieurs_mots(mots_cles):
    """
    Lance plusieurs recherches en parallèle.
    Retourne un dictionnaire :
    {
        "OpenAI": (resultats, maintenant),
        "Tesla": (...),
        ...
    }
    """

    resultats = {}

    with ThreadPoolExecutor(max_workers=min(8, len(mots_cles))) as executor:

        futures = {
            executor.submit(rechercher_tout, mot): mot
            for mot in mots_cles
        }

        for future in as_completed(futures):

            mot = futures[future]

            try:

                resultats[mot] = future.result()

            except Exception as e:

                print(f"Erreur pour {mot} : {e}")

                resultats[mot] = ([], datetime.now(timezone.utc))

    return resultats
