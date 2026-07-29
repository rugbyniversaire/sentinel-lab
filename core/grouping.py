import re

from core.constants import (
    MOTS_VIDES,
    SEUIL_SIMILARITE
)


def normaliser_titre(titre):

    mots = re.findall(
        r"[a-zàâäéèêëïîôöùûüç0-9]+",
        titre.lower()
    )

    return {
        m
        for m in mots
        if m not in MOTS_VIDES and len(m) > 2
    }


def similarite(mots_a, mots_b):

    if not mots_a or not mots_b:
        return 0

    intersection = len(mots_a & mots_b)

    union = len(mots_a | mots_b)

    jaccard = intersection / union if union else 0

    chevauchement = (
        intersection /
        min(len(mots_a), len(mots_b))
    )

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

            meilleur["elements"].append(resultat)

            meilleur["mots"] |= mots

        else:

            groupes.append({

                "mots": mots,

                "elements": [resultat]

            })

    return groupes


def synthetiser_titre(elements):

    if len(elements) == 1:
        return elements[0]["titre"]

    compte = {}

    casse = {}

    ordre = []

    for element in elements:

        mots = re.findall(
            r"[A-Za-zÀ-ÿ0-9]+",
            element["titre"]
        )

        vus = set()

        for mot in mots:

            normalise = mot.lower()

            if (
                normalise in MOTS_VIDES
                or len(normalise) <= 2
            ):
                continue

            if normalise not in vus:

                compte[normalise] = (
                    compte.get(normalise, 0)
                    + 1
                )

                vus.add(normalise)

            if normalise not in casse:

                casse[normalise] = mot

                ordre.append(normalise)

    seuil = max(
        2,
        (len(elements) + 1) // 2
    )

    mots = [

        m

        for m in ordre

        if compte.get(m, 0) >= seuil

    ]

    if not mots:

        mots = sorted(
            ordre,
            key=lambda x: -compte.get(x, 0)
        )[:6]

    mots = mots[:6]

    titre = " ".join(
        casse[m]
        for m in mots
    )

    return titre or elements[0]["titre"]
