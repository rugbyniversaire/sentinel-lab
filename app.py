import streamlit as st
import requests
import feedparser
import re
from datetime import datetime, timezone, timedelta
from urllib.parse import quote

st.set_page_config(page_title="Veille mot-clé", page_icon="🔍")
st.title("🔍 Outil de veille")
st.caption("Résultats publiés dans les dernières 24h, toutes sources confondues")

YOUTUBE_API_KEY = st.secrets.get("YOUTUBE_API_KEY", "")

if "mots_cles" not in st.session_state:
    st.session_state.mots_cles = []
from core.constants import LIMITE_HEURES, SEUIL_SIMILARITE, MOTS_VIDES

# ------------------- GESTION DES MOTS-CLES -------------------
st.subheader("Tes mots-clés suivis")

col1, col2 = st.columns([4, 1])
with col1:
    nouveau_mot_cle = st.text_input("Ajouter un mot-clé", label_visibility="collapsed", placeholder="Ajouter un mot-clé")
with col2:
    if st.button("Ajouter") and nouveau_mot_cle.strip():
        if nouveau_mot_cle.strip() not in st.session_state.mots_cles:
            st.session_state.mots_cles.append(nouveau_mot_cle.strip())
        st.rerun()

if not st.session_state.mots_cles:
    st.info("Aucun mot-clé ajouté pour l'instant.")
else:
    for mc in st.session_state.mots_cles:
        col_a, col_b = st.columns([5, 1])
        col_a.write(f"• {mc}")
        if col_b.button("🗑️", key=f"suppr_{mc}"):
            st.session_state.mots_cles.remove(mc)
            st.rerun()

st.divider()

col_lancer, col_filtre = st.columns([2, 2])
with col_lancer:
    lancer = st.button("Lancer la veille sur tous les mots-clés", disabled=not st.session_state.mots_cles)
with col_filtre:
    ne_garder_que_regroupes = st.checkbox("N'afficher que les sujets avec plusieurs sources", value=False)


# ------------------- REGROUPEMENT PAR SIMILARITE -------------------
from core.grouping import (
    regrouper_resultats,
    synthetiser_titre
)




# ------------------- FONCTIONS DE RECHERCHE -------------------

from core.utils import parser_date_iso, extraire_image_html
from core.filters import (
    est_recent,
    est_pertinent,
    dedupliquer
)






















def chercher_youtube(mot_cle, seuil):
    if not YOUTUBE_API_KEY:
        return []
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "key": YOUTUBE_API_KEY,
        "q": mot_cle,
        "part": "snippet",
        "type": "video",
        "order": "date",
        "maxResults": 25,
        "publishedAfter": seuil.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "relevanceLanguage": "fr",
    }
    try:
        reponse = requests.get(url, params=params, timeout=10)
        if reponse.status_code != 200:
            return []
        data = reponse.json()
        resultats = []
        for item in data.get("items", []):
            snippet = item.get("snippet", {})
            date_pub = parser_date_iso(snippet.get("publishedAt"))
            video_id = item.get("id", {}).get("videoId")
            titre_video = snippet.get("title", "")
            description = snippet.get("description", "")
            if est_recent(date_pub, seuil) and video_id and est_pertinent(mot_cle, titre_video + " " + description):
                miniatures = snippet.get("thumbnails", {})
                image = (miniatures.get("medium") or miniatures.get("default") or {}).get("url")
                resultats.append({
                    "source": "YouTube - " + snippet.get("channelTitle", ""),
                    "titre": titre_video,
                    "lien": f"https://www.youtube.com/watch?v={video_id}",
                    "date_pub": date_pub,
                    "image": image
                })
        return resultats
    except Exception:
        return []


def rechercher_tout(mot_cle):
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
    tous = [r for r in tous if est_pertinent(mot_cle, r["titre"])]
    tous = dedupliquer(tous)
    tous.sort(key=lambda r: r["date_pub"], reverse=True)
    return tous, maintenant


def afficher_resultats(resultats, maintenant, ne_garder_que_regroupes=False):
    if not resultats:
        st.warning(f"Aucun résultat publié dans les dernières {LIMITE_HEURES}h.")
        return

    groupes = regrouper_resultats(resultats)
    groupes.sort(key=lambda g: max(e["date_pub"] for e in g["elements"]), reverse=True)

    if ne_garder_que_regroupes:
        groupes = [g for g in groupes if len(g["elements"]) > 1]
        if not groupes:
            st.warning("Aucun sujet couvert par plusieurs sources pour l'instant. Décoche le filtre pour tout voir.")
            return

    st.success(f"{len(resultats)} résultat(s) trouvé(s), regroupés en {len(groupes)} sujet(s)")

    for groupe in groupes:
        elements = groupe["elements"]
        titre_groupe = synthetiser_titre(elements)
        plus_recent = max(e["date_pub"] for e in elements)
        age = maintenant - plus_recent
        heures = int(age.total_seconds() // 3600)
        minutes = int((age.total_seconds() % 3600) // 60)

        if len(elements) == 1:
            e = elements[0]
            col_img, col_texte = st.columns([1, 4]) if e.get("image") else (None, st)
            if col_img:
                with col_img:
                    st.image(e["image"], use_container_width=True)
                with col_texte:
                    st.markdown(f"**[{e['source']}]** {e['titre']}")
                    st.markdown(f"[{e['lien']}]({e['lien']}) — il y a {heures}h{minutes:02d}min")
            else:
                st.markdown(f"**[{e['source']}]** {e['titre']}")
                st.markdown(f"[{e['lien']}]({e['lien']}) — il y a {heures}h{minutes:02d}min")
        else:
            label = f"{titre_groupe}  —  🗞️ {len(elements)} articles (dernier il y a {heures}h{minutes:02d}min)"
            with st.expander(label):
                image_groupe = next((e.get("image") for e in elements if e.get("image")), None)
                if image_groupe:
                    st.image(image_groupe, width=320)
                for e in elements:
                    age_e = maintenant - e["date_pub"]
                    h_e = int(age_e.total_seconds() // 3600)
                    m_e = int((age_e.total_seconds() % 3600) // 60)
                    st.markdown(f"**[{e['source']}]** {e['titre']}")
                    st.markdown(f"[{e['lien']}]({e['lien']}) — il y a {h_e}h{m_e:02d}min")
                    st.markdown("")
        st.divider()


# ------------------- LANCEMENT -------------------
if lancer:
    if not YOUTUBE_API_KEY:
        st.info("Astuce : ajoute YOUTUBE_API_KEY dans les Secrets Streamlit pour inclure les vidéos YouTube.")
    for mc in st.session_state.mots_cles:
        st.subheader(f"Résultats pour « {mc} »")
        with st.spinner(f"Recherche pour « {mc} »..."):
            resultats, maintenant = rechercher_tout(mc)
        afficher_resultats(resultats, maintenant, ne_garder_que_regroupes)
