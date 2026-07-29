import streamlit as st

from core.constants import LIMITE_HEURES
from core.grouping import (
    regrouper_resultats,
    synthetiser_titre,
)


def afficher_resultats(
    resultats,
    maintenant,
    ne_garder_que_regroupes=False
):
    if not resultats:
        st.warning(
            f"Aucun résultat publié dans les dernières {LIMITE_HEURES}h."
        )
        return

    groupes = regrouper_resultats(resultats)

    groupes.sort(
        key=lambda g: max(
            e["date_pub"] for e in g["elements"]
        ),
        reverse=True
    )

    if ne_garder_que_regroupes:

        groupes = [
            g
            for g in groupes
            if len(g["elements"]) > 1
        ]

        if not groupes:
            st.warning(
                "Aucun sujet couvert par plusieurs sources."
            )
            return

    st.success(
        f"{len(resultats)} résultat(s) trouvés "
        f"regroupés en {len(groupes)} sujet(s)"
    )

    for groupe in groupes:

        elements = groupe["elements"]

        titre = synthetiser_titre(elements)

        plus_recent = max(
            e["date_pub"]
            for e in elements
        )

        age = maintenant - plus_recent

        heures = int(
            age.total_seconds() // 3600
        )

        minutes = int(
            (age.total_seconds() % 3600) // 60
        )

        # -----------------------------
        # CAS 1 : un seul résultat
        # -----------------------------

        if len(elements) == 1:

            e = elements[0]

            if e.get("image"):

                col_img, col_txt = st.columns(
                    [1, 4]
                )

                with col_img:
                    st.image(
                        e["image"],
                        use_container_width=True
                    )

                with col_txt:

                    st.markdown(
                        f"**{e['source']}**"
                    )

                    st.write(
                        e["titre"]
                    )

                    st.markdown(
                        f"[Ouvrir la source]({e['lien']})"
                    )

                    st.caption(
                        f"Publié il y a {heures}h{minutes:02d}"
                    )

            else:

                st.markdown(
                    f"**{e['source']}**"
                )

                st.write(
                    e["titre"]
                )

                st.markdown(
                    f"[Ouvrir la source]({e['lien']})"
                )

                st.caption(
                    f"Publié il y a {heures}h{minutes:02d}"
                )

        # -----------------------------
        # CAS 2 : plusieurs résultats
        # -----------------------------

        else:

            with st.expander(

                f"{titre} "
                f"({len(elements)} sources)"

            ):

                image = next(

                    (
                        e["image"]

                        for e in elements

                        if e.get("image")
                    ),

                    None

                )

                if image:

                    st.image(
                        image,
                        width=320
                    )

                for e in elements:

                    age = maintenant - e["date_pub"]

                    h = int(
                        age.total_seconds() // 3600
                    )

                    m = int(
                        (
                            age.total_seconds()
                            % 3600
                        ) // 60
                    )

                    st.markdown(
                        f"**{e['source']}**"
                    )

                    st.write(
                        e["titre"]
                    )

                    st.markdown(
                        f"[Ouvrir la source]({e['lien']})"
                    )

                    st.caption(
                        f"Publié il y a {h}h{m:02d}"
                    )

                    st.divider()

        st.divider()
