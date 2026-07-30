import streamlit as st

from core.constants import LIMITE_HEURES
from core.search_engine import rechercher_plusieurs_mots
from ui.display import afficher_resultats

# -------------------------------------------------
# CONFIGURATION
# -------------------------------------------------

st.set_page_config(
    page_title="Veille mot-clé",
    page_icon="🔍"
)

st.title("🔍 Outil de veille")

st.caption(
    f"Résultats publiés dans les dernières {LIMITE_HEURES} heures"
)

# -------------------------------------------------
# ETAT DE SESSION
# -------------------------------------------------

if "mots_cles" not in st.session_state:
    st.session_state.mots_cles = []

# -------------------------------------------------
# GESTION DES MOTS-CLES
# -------------------------------------------------

st.subheader("Tes mots-clés suivis")

col1, col2 = st.columns([4, 1])

with col1:

    nouveau = st.text_input(
        "Ajouter un mot-clé",
        label_visibility="collapsed",
        placeholder="Ajouter un mot-clé"
    )

with col2:

    if st.button("Ajouter"):

        if nouveau.strip():

            if nouveau.strip() not in st.session_state.mots_cles:

                st.session_state.mots_cles.append(
                    nouveau.strip()
                )

            st.rerun()

# -------------------------------------------------
# LISTE DES MOTS-CLES
# -------------------------------------------------

if not st.session_state.mots_cles:

    st.info(
        "Aucun mot-clé ajouté."
    )

else:

    for mot in st.session_state.mots_cles:

        c1, c2 = st.columns([5, 1])

        c1.write(f"• {mot}")

        if c2.button(
            "🗑️",
            key=f"supprimer_{mot}"
        ):

            st.session_state.mots_cles.remove(mot)

            st.rerun()

st.divider()

# -------------------------------------------------
# OPTIONS
# -------------------------------------------------

col1, col2 = st.columns(2)

with col1:

    lancer = st.button(
        "Lancer la veille",
        disabled=not st.session_state.mots_cles
    )

with col2:

    ne_garder_que_regroupes = st.checkbox(
        "Uniquement les sujets multi-sources",
        value=False
    )

# -------------------------------------------------
# RECHERCHE
# -------------------------------------------------

if lancer:

    with st.spinner("Recherche en cours..."):

        toutes_les_recherches = rechercher_plusieurs_mots(
            st.session_state.mots_cles
        )

    for mot in st.session_state.mots_cles:

        st.subheader(f"Résultats pour « {mot} »")

        resultats, maintenant = toutes_les_recherches[mot]

        afficher_resultats(
            resultats,
            maintenant,
            ne_garder_que_regroupes
        )
