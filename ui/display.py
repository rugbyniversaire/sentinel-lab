import streamlit as st

from core.grouping import (
    regrouper_resultats,
    synthetiser_titre
)

from core.constants import LIMITE_HEURES
from core.images import recuperer_image_article


def afficher_resultats(resultats, maintenant, ne_garder_que_regroupes=False):

    if not resultats:
        st.warning(f"Aucun résultat trouvé dans les dernières {LIMITE_HEURES} heures.")
        return

    groupes = regrouper_resultats(resultats)

    groupes.sort(
        key=lambda g: max(e["date_pub"] for e in g["elements"]),
        reverse=True,
    )

    if ne_garder_que_regroupes:

        groupes = [
            g for g in groupes
            if len(g["elements"]) > 1
        ]

        if not groupes:
            st.info("Aucun sujet couvert par plusieurs sources.")
            return

    st.success(
        f"{len(resultats)} résultat(s) regroupé(s) en {len(groupes)} sujet(s)"
    )

    for groupe in groupes:

        elements = groupe["elements"]

        titre = synthetiser_titre(elements)

        plus_recent = max(
            e["date_pub"] for e in elements
        )

        age = maintenant - plus_recent

        heures = int(age.total_seconds() // 3600)

        minutes = int((age.total_seconds() % 3600) // 60)

        # -----------------------------
        # IMAGE PRINCIPALE
        # -----------------------------

        image = None

        # 1. Image déjà présente dans les résultats
        for e in elements:

            if e.get("image"):

                image = e["image"]

                break

        # 2. Sinon récupération via OpenGraph
        if image is None:

            for e in elements:

                image = recuperer_image_article(
                    e["lien"]
                )

                if image:
                    break

        # -----------------------------
        # STATISTIQUES
        # -----------------------------

        nb_articles = len([
            e for e in elements
            if "YouTube" not in e["source"]
        ])

        nb_videos = len([
            e for e in elements
            if "YouTube" in e["source"]
        ])

        nb_sources = len({
            e["source"] for e in elements
        })

        # -----------------------------
        # CARTE PRINCIPALE
        # -----------------------------

        with st.container(border=True):

            if image:

                st.image(
                    image,
                    use_container_width=True
                )

            st.subheader(titre)

            badges = []

            if nb_articles:
                badges.append(
                    f"📰 {nb_articles} article(s)"
                )

            if nb_videos:
                badges.append(
                    f"📺 {nb_videos} vidéo(s)"
                )

            badges.append(
                f"🌐 {nb_sources} source(s)"
            )

            badges.append(
                f"⏱ {heures}h{minutes:02d}"
            )

            st.caption(" • ".join(badges))

            st.markdown("---")

            # -----------------------------
            # DETAIL DES SOURCES
            # -----------------------------

            with st.expander("Voir les sources"):

                for e in elements:

                    cols = st.columns([1, 5])

                    with cols[0]:

                        if e.get("image"):

                            st.image(
                                e["image"],
                                width=80
                            )

                    with cols[1]:

                        st.markdown(
                            f"### {e['source']}"
                        )

                        st.markdown(
                            f"**{e['titre']}**"
                        )

                        st.markdown(
                            f"[🔗 Ouvrir l'article]({e['lien']})"
                        )

                        age_source = maintenant - e["date_pub"]

                        h = int(age_source.total_seconds() // 3600)

                        m = int(
                            (age_source.total_seconds() % 3600) // 60
                        )

                        st.caption(
                            f"Publié il y a {h}h{m:02d}"
                        )

                        st.markdown("---")
