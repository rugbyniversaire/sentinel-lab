from .google_news import chercher_google_news
from .reddit import chercher_reddit
from .hackernews import chercher_hackernews
from .mastodon import chercher_mastodon
from .bluesky import chercher_bluesky
from .youtube import chercher_youtube

CONNECTEURS = [
    chercher_google_news,
    chercher_reddit,
    chercher_hackernews,
    chercher_mastodon,
    chercher_bluesky,
    chercher_youtube,
]
