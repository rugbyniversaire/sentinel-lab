import streamlit as st

from core.search_engine import rechercher_tout
from ui.display import afficher_resultats


st.set_page_config(
    page_title="Veille mot-clé",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Sentinel Lab")
st.caption("Résultats publiés dans les dernières 24 heures")


# ============================
# SESSION
# ============================

if "mots_cles" not in st.session_state:
    st.session_state.mots_cles = []


# ============================
# GESTION DES MOTS-CLES
# ============================

st.subheader("Mots-clés suivis")

col1, col2 = st.columns([4, 1])

with col1:
    nouveau_mot_cle = st.text_input(
        "Ajouter un mot-clé",
        placeholder="Ex : Intelligence artificielle",
        label_visibility="collapsed"
    )

with col2:
    if st.button("Ajouter"):
        mot = nouveau_mot_cle.strip()

        if mot:

            if mot not in st.session_state.mots_cles:
                st.session_state.mots_cles.append(mot)

            st.rerun()


if not st.session_state.mots_cles:

    st.info("Aucun mot-clé ajouté.")

else:

    for mot in st.session_state.mots_cles:

        c1, c2 = st.columns([6, 1])

        c1.write(f"• {mot}")

        if c2.button("🗑️", key=f"delete_{mot}"):

            st.session_state.mots_cles.remove(mot)

            st.rerun()


st.divider()


# ============================
# OPTIONS
# ============================

col1, col2 = st.columns([2, 3])

with col1:

    lancer = st.button(
        "Lancer la veille",
        use_container_width=True,
        disabled=len(st.session_state.mots_cles) == 0
    )

with col2:

    ne_garder_que_regroupes = st.checkbox(
        "Afficher uniquement les sujets présents dans plusieurs sources",
        value=False
    )


# ============================
# LANCEMENT
# ============================

if lancer:

    for mot in st.session_state.mots_cles:

        st.subheader(f"Résultats : {mot}")

        with st.spinner("Recherche en cours..."):

            resultats, maintenant = rechercher_tout(mot)

        afficher_resultats(
            resultats=resultats,
            maintenant=maintenant,
            ne_garder_que_regroupes=ne_garder_que_regroupes
        )
