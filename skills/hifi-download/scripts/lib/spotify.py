"""Spotify service for music search and user data."""

from typing import Optional, Literal
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from .config import SpotifyConfig


class SpotifyService:
    """Service for Spotify API."""

    def __init__(self, config: SpotifyConfig):
        self.config = config
        self._client: Optional[spotipy.Spotify] = None
        self._auth_client: Optional[spotipy.Spotify] = None

    def _get_client(self) -> spotipy.Spotify:
        """Get public data client."""
        if not self._client:
            if not self.config.is_configured():
                raise ValueError("Spotify not configured. Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET.")
            auth = SpotifyClientCredentials(
                client_id=self.config.client_id,
                client_secret=self.config.client_secret
            )
            self._client = spotipy.Spotify(auth_manager=auth)
        return self._client

    def _get_auth_client(self) -> spotipy.Spotify:
        """Get authenticated client for user data."""
        if not self._auth_client:
            if not self.config.is_configured():
                raise ValueError("Spotify not configured.")
            auth = SpotifyOAuth(
                client_id=self.config.client_id,
                client_secret=self.config.client_secret,
                redirect_uri=self.config.redirect_uri,
                scope="user-library-read user-top-read"
            )
            self._auth_client = spotipy.Spotify(auth_manager=auth)
        return self._auth_client

    @staticmethod
    def _format_duration(ms: int) -> str:
        """Format milliseconds to M:SS string."""
        return f"{ms // 60000}:{(ms % 60000) // 1000:02d}"

    def search(
        self,
        query: str,
        search_type: str = "track",
        limit: int = 10,
        market: str = "US",
    ) -> dict:
        """Search Spotify. Returns structured dict."""
        client = self._get_client()
        results = client.search(q=query, type=search_type, limit=limit, market=market)

        key = f"{search_type}s"
        items = results.get(key, {}).get("items", [])

        parsed = []
        for item in items:
            if search_type == "track":
                artists = ", ".join([a["name"] for a in item["artists"]])
                parsed.append({
                    "name": item["name"],
                    "artists": artists,
                    "id": item["id"],
                    "album": item["album"]["name"],
                    "duration": self._format_duration(item["duration_ms"]),
                    "url": item["external_urls"]["spotify"],
                })
            elif search_type == "album":
                artists = ", ".join([a["name"] for a in item["artists"]])
                parsed.append({
                    "name": item["name"],
                    "artists": artists,
                    "id": item["id"],
                    "release_date": item["release_date"],
                    "total_tracks": item["total_tracks"],
                    "url": item["external_urls"]["spotify"],
                })
            elif search_type == "artist":
                parsed.append({
                    "name": item["name"],
                    "id": item["id"],
                    "genres": ", ".join(item.get("genres", [])) or "No genres",
                    "popularity": item.get("popularity", 0),
                    "url": item["external_urls"]["spotify"],
                })

        return {
            "results": parsed,
            "total": len(parsed),
            "query": query,
            "search_type": search_type,
        }

    def get_info(
        self,
        item_id: str,
        item_type: Literal["track", "album", "artist"],
    ) -> dict:
        """Get item details. Returns structured dict."""
        client = self._get_client()

        if item_type == "track":
            track = client.track(item_id)
            artists = ", ".join([a["name"] for a in track["artists"]])
            return {
                "name": track["name"],
                "artists": artists,
                "album": track["album"]["name"],
                "duration": self._format_duration(track["duration_ms"]),
                "popularity": track.get("popularity", 0),
                "id": track["id"],
                "url": track["external_urls"]["spotify"],
            }

        elif item_type == "album":
            album = client.album(item_id)
            artists = ", ".join([a["name"] for a in album["artists"]])
            genres = ", ".join(album.get("genres", [])) or "No genres"
            tracks = []
            for t in album["tracks"]["items"]:
                tracks.append({
                    "name": t["name"],
                    "duration": self._format_duration(t["duration_ms"]),
                    "id": t["id"],
                })
            return {
                "name": album["name"],
                "artists": artists,
                "release_date": album["release_date"],
                "total_tracks": album["total_tracks"],
                "genres": genres,
                "id": album["id"],
                "url": album["external_urls"]["spotify"],
                "tracks": tracks,
            }

        elif item_type == "artist":
            artist = client.artist(item_id)
            top = client.artist_top_tracks(item_id)
            genres = ", ".join(artist.get("genres", [])) or "No genres"
            top_tracks = []
            for t in top["tracks"][:10]:
                top_tracks.append({
                    "name": t["name"],
                    "album": t["album"]["name"],
                    "id": t["id"],
                })
            return {
                "name": artist["name"],
                "genres": genres,
                "popularity": artist.get("popularity", 0),
                "followers": artist["followers"]["total"],
                "id": artist["id"],
                "url": artist["external_urls"]["spotify"],
                "top_tracks": top_tracks,
            }

    def get_user_data(
        self,
        data_type: Literal["tracks", "artists"],
        time_range: str = "medium_term",
        limit: int = 20,
    ) -> dict:
        """Get user's top tracks or artists. Returns structured dict."""
        client = self._get_auth_client()

        time_desc = {
            "short_term": "last 4 weeks",
            "medium_term": "last 6 months",
            "long_term": "all time"
        }.get(time_range, time_range)

        parsed = []
        if data_type == "tracks":
            results = client.current_user_top_tracks(time_range=time_range, limit=limit)
            for track in results.get("items", []):
                artists = ", ".join([a["name"] for a in track["artists"]])
                parsed.append({
                    "name": track["name"],
                    "artists": artists,
                    "id": track["id"],
                    "album": track["album"]["name"],
                })
        elif data_type == "artists":
            results = client.current_user_top_artists(time_range=time_range, limit=limit)
            for artist in results.get("items", []):
                parsed.append({
                    "name": artist["name"],
                    "id": artist["id"],
                    "genres": ", ".join(artist.get("genres", [])) or "No genres",
                    "popularity": artist.get("popularity", 0),
                })

        return {
            "results": parsed,
            "total": len(parsed),
            "data_type": data_type,
            "time_range": time_range,
            "time_desc": time_desc,
        }
