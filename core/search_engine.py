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
