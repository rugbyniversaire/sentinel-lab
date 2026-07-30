from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone, timedelta

from core.constants import LIMITE_HEURES
from core.filters import est_pertinent, dedupliquer

from connectors import CONNECTEURS


def rechercher_tout(mot_cle):
    """
    Recherche un mot-clé sur tous les connecteurs,
    eux-mêmes lancés en parallèle.
    """

    maintenant = datetime.now(timezone.utc)

    seuil = maintenant - timedelta(hours=LIMITE_HEURES)

    tous = []

    with ThreadPoolExecutor(max_workers=len(CONNECTEURS)) as executor:

        futures = {
            executor.submit(connecteur, mot_cle, seuil): connecteur.__name__
            for connecteur in CONNECTEURS
        }

        for future in as_completed(futures):

            try:

                resultats = future.result()

                tous.extend(resultats)

            except Exception as e:

                print(f"Erreur connecteur {futures[future]} : {e}")

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
    Recherche plusieurs mots-clés en parallèle.
    """

    resultats = {}

    with ThreadPoolExecutor(
        max_workers=min(len(mots_cles), 8)
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

                print(f"Erreur {mot} : {e}")

                resultats[mot] = (
                    [],
                    datetime.now(timezone.utc)
                )

    return resultats
