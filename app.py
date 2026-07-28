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































# ------------------- LANCEMENT -------------------
if lancer:
    if not YOUTUBE_API_KEY:
        st.info("Astuce : ajoute YOUTUBE_API_KEY dans les Secrets Streamlit pour inclure les vidéos YouTube.")
    for mc in st.session_state.mots_cles:
        st.subheader(f"Résultats pour « {mc} »")
        with st.spinner(f"Recherche pour « {mc} »..."):
            resultats, maintenant = rechercher_tout(mc)
        afficher_resultats(resultats, maintenant, ne_garder_que_regroupes)
