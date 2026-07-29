import re


def est_recent(date_publication, seuil):
    if date_publication is None:
        return False
    return date_publication >= seuil


def est_pertinent(mot_cle, texte):

    mots_cle = [
        m
        for m in re.findall(
            r"[a-zàâäéèêëïîôöùûüç0-9]+",
            mot_cle.lower()
        )
        if len(m) > 2
    ]

    if not mots_cle:
        return True

    texte = texte.lower()

    trouves = sum(
        1
        for mot in mots_cle
        if mot in texte
    )

    seuil_requis = max(
        1,
        round(len(mots_cle) * 0.6)
    )

    return trouves >= seuil_requis


def dedupliquer(resultats):

    vus = set()

    uniques = []

    for r in resultats:

        cle = (
            (r["lien"] or "")
            + "|"
            + r["titre"].strip().lower()
        )

        if cle in vus:
            continue

        vus.add(cle)

        uniques.append(r)

    return uniques
