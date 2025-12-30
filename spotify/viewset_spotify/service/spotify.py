from django.conf import settings
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from rest_framework.response import Response

import requests


def get_spotify_oauth():
    return SpotifyOAuth(
        client_id=settings.CLIENT_ID,
        client_secret=settings.CLIENT_SECRET,
        redirect_uri=settings.REDIRECT_URI,
        scope="user-read-email user-read-private",
        cache_path=None  # 👈 IMPORTANTE
    )

def get_auth_url():
    sp_auth = get_spotify_oauth()
    auth_url = sp_auth.get_authorize_url()
    return auth_url

def get_spotify_token():
    sp_auth = get_spotify_oauth()
    token_info = sp_auth.get_cached_token()
    return token_info

def get_user_profile(token):
    url = "https://api.spotify.com/v1/me"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    return None

def get_top_tracks(token):
    url = "https://api.spotify.com/v1/me/top/tracks"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    return None