import re

from core.constants import MOTS_VIDES, SEUIL_SIMILARITE

def normaliser_titre(titre):
    mots = re.findall(r"[a-zàâäéèêëïîôöùûüç0-9]+", titre.lower())
    return {m for m in mots if m not in MOTS_VIDES and len(m) > 2}


def similarite(mots_a, mots_b):
    if not mots_a or not mots_b:
        return 0
    intersection = len(mots_a & mots_b)
    union = len(mots_a | mots_b)
    jaccard = intersection / union if union else 0
    chevauchement = intersection / min(len(mots_a), len(mots_b))
    return max(jaccard, chevauchement)


def regrouper_resultats(resultats):
    groupes = []
    for r in resultats:
        mots_titre = normaliser_titre(r["titre"])
        meilleur_groupe = None
        meilleur_score = 0
        for groupe in groupes:
            score = similarite(mots_titre, groupe["mots"])
            if score > SEUIL_SIMILARITE and score > meilleur_score:
                meilleur_groupe = groupe
                meilleur_score = score
        if meilleur_groupe:
            meilleur_groupe["elements"].append(r)
            meilleur_groupe["mots"] |= mots_titre
        else:
            groupes.append({"mots": mots_titre, "elements": [r]})
    return groupes


def synthetiser_titre(elements):
    if len(elements) == 1:
        return elements[0]["titre"]

    compte = {}
    casse_originale = {}
    ordre_apparition = []

    for e in elements:
        mots_bruts = re.findall(r"[A-Za-zÀ-ÿ0-9]+", e["titre"])
        vus_dans_ce_titre = set()
        for m in mots_bruts:
            m_norm = m.lower()
            if m_norm in MOTS_VIDES or len(m_norm) <= 2:
                continue
            if m_norm not in vus_dans_ce_titre:
                compte[m_norm] = compte.get(m_norm, 0) + 1
                vus_dans_ce_titre.add(m_norm)
            if m_norm not in casse_originale:
                casse_originale[m_norm] = m
                ordre_apparition.append(m_norm)

    seuil_frequence = max(2, (len(elements) + 1) // 2)
    mots_choisis = [m for m in ordre_apparition if compte.get(m, 0) >= seuil_frequence]

    if not mots_choisis:
        mots_choisis = sorted(ordre_apparition, key=lambda m: -compte.get(m, 0))[:6]

    mots_choisis = mots_choisis[:6]
    titre = " ".join(casse_originale[m] for m in mots_choisis)
    return titre if titre else elements[0]["titre"]
