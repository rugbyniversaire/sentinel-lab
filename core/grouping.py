import re

from core.constants import MOTS_VIDES, SEUIL_SIMILARITE


def normaliser_titre(titre):
    mots = re.findall(
        r"[A-Za-zÀ-ÿ0-9]+",
        titre.lower()
    )

    return {
        m
        for m in mots
        if len(m) > 2
        and m not in MOTS_VIDES
    }


def similarite(a, b):

    if not a or not b:
        return 0

    intersection = len(a & b)

    union = len(a | b)

    jaccard = intersection / union

    chevauchement = intersection / min(len(a), len(b))

    return max(
        jaccard,
        chevauchement
    )


def regrouper_resultats(resultats):

    groupes = []

    for resultat in resultats:

        mots = normaliser_titre(
            resultat["titre"]
        )

        meilleur = None

        meilleur_score = 0

        for groupe in groupes:

            score = similarite(
                mots,
                groupe["mots"]
            )

            if (
                score > SEUIL_SIMILARITE
                and score > meilleur_score
            ):

                meilleur = groupe

                meilleur_score = score

        if meilleur:

            meilleur["elements"].append(
                resultat
            )

            meilleur["mots"] |= mots

        else:

            groupes.append({

                "mots": mots,

                "elements": [resultat]

            })

    return groupes


def synthetiser_titre(elements):
    """
    Génère automatiquement un titre représentatif
    du groupe d'articles.
    """

    if len(elements) == 1:
        return elements[0]["titre"]

    compteur = {}

    casse = {}

    for article in elements:

        titre = article.get("titre", "")

        mots = re.findall(
            r"[A-Za-zÀ-ÿ0-9]+",
            titre
        )

        deja = set()

        for mot in mots:

            m = mot.lower()

            if (
                len(m) <= 2
                or m in MOTS_VIDES
            ):
                continue

            if m not in deja:

                compteur[m] = compteur.get(m, 0) + 1

                deja.add(m)

            if m not in casse:

                casse[m] = mot

    if not compteur:
        return "Sujet d'actualité"

    # mots classés par fréquence
    mots = sorted(
        compteur,
        key=lambda x: (
            compteur[x],
            len(x)
        ),
        reverse=True
    )

    # on garde les 6 premiers
    mots = mots[:6]

    titre = " ".join(
        casse[m]
        for m in mots
    )

    return titre
