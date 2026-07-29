import requests
import streamlit as st

from core.filters import (
    est_recent,
    est_pertinent
)

from core.utils import parser_date_iso


YOUTUBE_API_KEY = st.secrets.get(
    "YOUTUBE_API_KEY",
    ""
)


def chercher_youtube(mot_cle, seuil):

    if not YOUTUBE_API_KEY:
        return []

    url = (
        "https://www.googleapis.com/youtube/v3/search"
    )

    params = {

        "key": YOUTUBE_API_KEY,

        "q": mot_cle,

        "part": "snippet",

        "type": "video",

        "order": "date",

        "maxResults": 25,

        "publishedAfter": seuil.strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        ),

        "relevanceLanguage": "fr"

    }

    try:

        reponse = requests.get(
            url,
            params=params,
            timeout=10
        )

        if reponse.status_code != 200:
            return []

        data = reponse.json()

        resultats = []

        for item in data.get("items", []):

            snippet = item["snippet"]

            date_pub = parser_date_iso(
                snippet.get("publishedAt")
            )

            titre = snippet.get("title", "")

            description = snippet.get(
                "description",
                ""
            )

            video_id = item["id"].get(
                "videoId"
            )

            if (
                est_recent(date_pub, seuil)
                and video_id
                and est_pertinent(
                    mot_cle,
                    titre + " " + description
                )
            ):

                miniatures = snippet.get(
                    "thumbnails",
                    {}
                )

                image = (
                    miniatures.get("medium")
                    or miniatures.get("default")
                    or {}
                ).get("url")

                resultats.append({

                    "source": "YouTube - "
                    + snippet.get(
                        "channelTitle",
                        ""
                    ),

                    "titre": titre,

                    "lien": (
                        f"https://www.youtube.com/watch?v={video_id}"
                    ),

                    "date_pub": date_pub,

                    "image": image

                })

        return resultats

    except Exception:

        return []
