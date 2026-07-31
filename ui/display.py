import streamlit as st

from core.grouping import regrouper_resultats
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

        elements = sorted(
            groupe["elements"],
            key=lambda e: e["date_pub"],
            reverse=True
        )

        principal = elements[0]

        titre = principal.get("titre") or "Sans titre"

        media = principal.get("media", principal.get("source", ""))

        description = principal.get("description", "")

        image = principal.get("image")

        if not image:
            image = recuperer_image_article(
                principal["lien"]
            )

        age = maintenant - principal["date_pub"]

        heures = int(age.total_seconds() // 3600)

        minutes = int(
            (age.total_seconds() % 3600) // 60
        )

        nb_articles = len([
            e for e in elements
            if "YouTube" not in e["source"]
        ])

        nb_videos = len([
            e for e in elements
            if "YouTube" in e["source"]
        ])

        nb_sources = len({
            e["source"]
            for e in elements
        })

        with st.container(border=True):

            if image:

                st.image(
                    image,
                    use_container_width=True
                )

            st.markdown(f"## {titre}")

            st.caption(
                f"📰 {media} • ⏱️ {heures}h{minutes:02d}"
            )

            if description:

                st.write(description)

            badges = []

            if nb_articles:
                badges.append(f"📰 {nb_articles} article(s)")

            if nb_videos:
                badges.append(f"📺 {nb_videos} vidéo(s)")

            badges.append(f"🌐 {nb_sources} source(s)")

            st.caption(" • ".join(badges))

            st.link_button(
                "🔗 Lire l'article principal",
                principal["lien"],
                use_container_width=True
            )

            if len(elements) > 1:

                st.divider()

                with st.expander(f"Voir les {len(elements)} sources"):

                    for e in elements:

                        cols = st.columns([1, 4])

                        with cols[0]:

                            if e.get("image"):

                                st.image(
                                    e["image"],
                                    width=100
                                )

                        with cols[1]:

                            st.markdown(
                                f"**{e.get('media', e['source'])}**"
                            )

                            st.markdown(
                                e["titre"]
                            )

                            st.link_button(
                                "Ouvrir",
                                e["lien"],
                                key=e["lien"]
                            )

                            age2 = maintenant - e["date_pub"]

                            h = int(age2.total_seconds() // 3600)

                            m = int(
                                (age2.total_seconds() % 3600) // 60
                            )

                            st.caption(
                                f"Publié il y a {h}h{m:02d}"
                            )

                            st.divider()
