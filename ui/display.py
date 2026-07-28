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
