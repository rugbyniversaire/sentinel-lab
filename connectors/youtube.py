def chercher_youtube(mot_cle, seuil):
    if not YOUTUBE_API_KEY:
        return []
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "key": YOUTUBE_API_KEY,
        "q": mot_cle,
        "part": "snippet",
        "type": "video",
        "order": "date",
        "maxResults": 25,
        "publishedAfter": seuil.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "relevanceLanguage": "fr",
    }
    try:
        reponse = requests.get(url, params=params, timeout=10)
        if reponse.status_code != 200:
            return []
        data = reponse.json()
        resultats = []
        for item in data.get("items", []):
            snippet = item.get("snippet", {})
            date_pub = parser_date_iso(snippet.get("publishedAt"))
            video_id = item.get("id", {}).get("videoId")
            titre_video = snippet.get("title", "")
            description = snippet.get("description", "")
            if est_recent(date_pub, seuil) and video_id and est_pertinent(mot_cle, titre_video + " " + description):
                miniatures = snippet.get("thumbnails", {})
                image = (miniatures.get("medium") or miniatures.get("default") or {}).get("url")
                resultats.append({
                    "source": "YouTube - " + snippet.get("channelTitle", ""),
                    "titre": titre_video,
                    "lien": f"https://www.youtube.com/watch?v={video_id}",
                    "date_pub": date_pub,
                    "image": image
                })
        return resultats
    except Exception:
        return []
