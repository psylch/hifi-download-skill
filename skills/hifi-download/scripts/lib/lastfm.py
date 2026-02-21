"""Last.fm service for music discovery."""

from typing import List, Tuple
import requests


class LastfmService:
    """Service for Last.fm API."""

    BASE_URL = "http://ws.audioscrobbler.com/2.0/"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def _request(self, params: dict) -> dict:
        """Make API request."""
        params["api_key"] = self.api_key
        params["format"] = "json"
        try:
            resp = requests.get(self.BASE_URL, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            if "error" in data:
                raise ValueError(data.get("message", "Unknown Last.fm API error"))
            return data
        except requests.RequestException as e:
            raise ValueError(f"Last.fm API error: {e}")

    def get_similar_artists(self, artist: str, limit: int = 10) -> dict:
        """Get similar artists. Returns structured dict."""
        data = self._request({
            "method": "artist.getSimilar",
            "artist": artist,
            "limit": min(limit, 100),
            "autocorrect": 1
        })

        artists = data.get("similarartists", {}).get("artist", [])
        results = []
        for a in artists:
            match = int(float(a.get("match", 0)) * 100)
            entry = {
                "name": a.get("name", "Unknown"),
                "similarity": match,
            }
            if a.get("mbid"):
                entry["mbid"] = a["mbid"]
            if a.get("url"):
                entry["url"] = a["url"]
            results.append(entry)

        return {
            "results": results,
            "total": len(results),
            "query_artist": artist
        }

    def get_similar_tracks(self, track: str, artist: str, limit: int = 10) -> dict:
        """Get similar tracks. Returns structured dict."""
        data = self._request({
            "method": "track.getSimilar",
            "track": track,
            "artist": artist,
            "limit": min(limit, 100),
            "autocorrect": 1
        })

        tracks = data.get("similartracks", {}).get("track", [])
        results = []
        for t in tracks:
            match = int(float(t.get("match", 0)) * 100)
            name = t.get("name", "Unknown")
            artist_name = t.get("artist", {}).get("name", "Unknown")
            entry = {
                "name": name,
                "artist": artist_name,
                "similarity": match,
            }
            duration_ms = t.get("duration", 0)
            if duration_ms and int(duration_ms) > 0:
                secs = int(duration_ms) // 1000
                entry["duration"] = f"{secs // 60}:{secs % 60:02d}"
            if t.get("url"):
                entry["url"] = t["url"]
            results.append(entry)

        return {
            "results": results,
            "total": len(results),
            "query_track": track,
            "query_artist": artist
        }

    def discover_from_taste(
        self,
        top_artists: List[str],
        top_tracks: List[Tuple[str, str]],  # (track, artist) pairs
        limit_per_item: int = 5
    ) -> dict:
        """Discover music based on user's taste. Returns structured dict."""
        similar_artists = {}
        for artist in top_artists[:3]:
            try:
                result = self.get_similar_artists(artist, limit_per_item)
                similar_artists[artist] = result["results"]
            except Exception:
                similar_artists[artist] = []

        similar_tracks = {}
        for track_name, artist_name in top_tracks[:3]:
            key = f"{track_name} by {artist_name}"
            try:
                result = self.get_similar_tracks(track_name, artist_name, limit_per_item)
                similar_tracks[key] = result["results"]
            except Exception:
                similar_tracks[key] = []

        return {
            "similar_artists": similar_artists,
            "similar_tracks": similar_tracks
        }
