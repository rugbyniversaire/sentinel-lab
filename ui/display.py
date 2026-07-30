import streamlit as st

from core.grouping import (
    regrouper_resultats,
    synthetiser_titre
)

from core.constants import LIMITE_HEURES


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

            st.info(
                "Aucun sujet multi-sources."
            )

            return

    st.success(
        f"{len(groupes)} sujet(s) détecté(s)"
    )

    for groupe in groupes:

        elements = groupe["elements"]

        titre = synthetiser_titre(elements)

        plus_recent = max(
            e["date_pub"] for e in elements
        )

        age = maintenant - plus_recent

        heures = int(age.total_seconds() // 3600)

        minutes = int(
            (age.total_seconds() % 3600) // 60
        )

        image = next(
            (
                e.get("image")
                for e in elements
                if e.get("image")
            ),
            None,
        )

        nb_articles = len(
            [
                e for e in elements
                if "YouTube" not in e["source"]
            ]
        )

        nb_videos = len(
            [
                e for e in elements
                if "YouTube" in e["source"]
            ]
        )

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
                f"⏱ {heures}h{minutes:02d}"
            )

            st.caption(" • ".join(badges))

            st.markdown("---")

            for e in elements:

                cols = st.columns([1, 8])

                with cols[0]:

                    if e.get("image"):

                        st.image(
                            e["image"],
                            width=80
                        )

                with cols[1]:

                    st.markdown(
                        f"**{e['source']}**"
                    )

                    st.markdown(
                        f"[{e['titre']}]({e['lien']})"
                    )

            st.write("")
