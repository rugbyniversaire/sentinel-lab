def est_recent(date_publication, seuil):
    if date_publication is None:
        return False
    return date_publication >= seuil



