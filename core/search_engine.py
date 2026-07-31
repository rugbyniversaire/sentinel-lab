from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone, timedelta

from core.constants import LIMITE_HEURES
from core.filters import est_pertinent, dedupliquer
from core.enrich import enrichir_resultat

from connectors.google_news import chercher_google_news
from connectors.reddit import chercher_reddit
from connectors.hackernews import chercher_hackernews
from connectors.mastodon import chercher_mastodon
from connectors.bluesky import chercher_bluesky
from connectors.youtube import chercher_youtube


CONNECTEURS = [
    chercher_google_news,
    chercher_reddit,
    chercher_hackernews,
    chercher_mastodon,
    chercher_bluesky,
    chercher_youtube,
]


def rechercher_tout(mot_cle):

    maintenant = datetime.now(timezone.utc)

    seuil = maintenant - timedelta(hours=LIMITE_HEURES)

    tous = []

    with ThreadPoolExecutor(
        max_workers=len(CONNECTEURS)
    ) as executor:

        futures = {
            executor.submit(
                connecteur,
                mot_cle,
                seuil
            ): connecteur.__name__
            for connecteur in CONNECTEURS
        }

        for future in as_completed(futures):

            try:

                tous.extend(
                    future.result()
                )

            except Exception as e:

                print(
                    f"Erreur {futures[future]} : {e}"
                )

    tous = [
        r
        for r in tous
        if est_pertinent(
            mot_cle,
            r["titre"]
        )
    ]

    tous = dedupliquer(tous)

    # enrichissement des résultats
    print("Avant enrichissement :", len(tous))
    tous = [
        enrichir_resultat(r)
        for r in tous
    ]
    print("Après enrichissement :", len(tous))
    

    tous.sort(
        key=lambda r: r["date_pub"],
        reverse=True
    )

    return tous, maintenant


def rechercher_plusieurs_mots(mots_cles):

    resultats = {}

    with ThreadPoolExecutor(
        max_workers=min(
            len(mots_cles),
            8
        )
    ) as executor:

        futures = {
            executor.submit(
                rechercher_tout,
                mot
            ): mot
            for mot in mots_cles
        }

        for future in as_completed(futures):

            mot = futures[future]

            try:

                resultats[mot] = future.result()

            except Exception as e:

                print(
                    f"Erreur {mot} : {e}"
                )

                resultats[mot] = (
                    [],
                    datetime.now(timezone.utc)
                )

    return resultats
