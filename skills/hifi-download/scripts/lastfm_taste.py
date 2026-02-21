#!/usr/bin/env python3
"""Get personalized music recommendations based on Spotify listening history."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from lib.config import Config
from lib.spotify import SpotifyService
from lib.lastfm import LastfmService
from lib.output import ok, fail


def extract_artists(data: dict) -> list:
    """Extract artist names from spotify user data."""
    return [r["name"] for r in data.get("results", [])]


def extract_tracks(data: dict) -> list:
    """Extract (track, artist) tuples from spotify user data."""
    return [(r["name"], r["artists"]) for r in data.get("results", [])]


def main():
    parser = argparse.ArgumentParser(
        description="Get personalized recommendations based on your listening history"
    )
    parser.add_argument("-r", "--range", dest="time_range",
                        choices=["short_term", "medium_term", "long_term"],
                        default="medium_term",
                        help="Time range for listening history")
    parser.add_argument("-n", "--per-item", type=int, default=5,
                        help="Recommendations per seed item (default: 5)")
    args = parser.parse_args()

    config = Config.load()

    if not config.spotify.is_configured():
        fail("Spotify not configured", hint="Run setup_config.py with Spotify credentials", recoverable=False)
    if not config.lastfm.is_configured():
        fail("Last.fm API key not configured", hint="Run setup_config.py with --lastfm-key=KEY", recoverable=False)

    try:
        spotify = SpotifyService(config.spotify)

        top_artists_data = spotify.get_user_data("artists", args.time_range, 5)
        top_artists = extract_artists(top_artists_data)

        top_tracks_data = spotify.get_user_data("tracks", args.time_range, 5)
        top_tracks = extract_tracks(top_tracks_data)

        if not top_artists and not top_tracks:
            ok({"results": [], "total": 0},
               hint="No listening history found. Listen to more music on Spotify first!")
            return

        lastfm = LastfmService(config.lastfm.api_key)
        result = lastfm.discover_from_taste(top_artists, top_tracks, args.per_item)

        total_artists = sum(len(v) for v in result["similar_artists"].values())
        total_tracks = sum(len(v) for v in result["similar_tracks"].values())

        ok(result, hint=f"Discovered {total_artists} similar artists and {total_tracks} similar tracks based on your taste")

    except ValueError as e:
        fail(str(e), hint="Check your API keys and network connection")


if __name__ == "__main__":
    main()
