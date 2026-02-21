#!/usr/bin/env python3
"""Get detailed information about a Spotify item."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from lib.config import Config
from lib.output import ok, fail
from lib.spotify import SpotifyService


def format_text(data: dict, item_type: str) -> str:
    """Format item info as human-readable text."""
    if item_type == "track":
        return (f"Track: {data['name']}\n"
                f"Artist(s): {data['artists']}\n"
                f"Album: {data['album']}\n"
                f"Duration: {data['duration']}\n"
                f"Popularity: {data['popularity']}/100\n"
                f"Spotify ID: {data['id']}\n"
                f"URL: {data['url']}")

    elif item_type == "album":
        tracks = "\n".join(
            f"  {i}. {t['name']} ({t['duration']}) [ID: {t['id']}]"
            for i, t in enumerate(data.get("tracks", []), 1)
        )
        return (f"Album: {data['name']}\n"
                f"Artist(s): {data['artists']}\n"
                f"Release: {data['release_date']}\n"
                f"Tracks: {data['total_tracks']}\n"
                f"Genres: {data['genres']}\n"
                f"Spotify ID: {data['id']}\n"
                f"URL: {data['url']}\n\n"
                f"Tracklist:\n{tracks}")

    elif item_type == "artist":
        top_tracks = "\n".join(
            f"  {i}. {t['name']} (from {t['album']}) [ID: {t['id']}]"
            for i, t in enumerate(data.get("top_tracks", []), 1)
        )
        return (f"Artist: {data['name']}\n"
                f"Genres: {data['genres']}\n"
                f"Popularity: {data['popularity']}/100\n"
                f"Followers: {data['followers']:,}\n"
                f"Spotify ID: {data['id']}\n"
                f"URL: {data['url']}\n\n"
                f"Top Tracks:\n{top_tracks}")


def main():
    parser = argparse.ArgumentParser(description="Get Spotify item details")
    parser.add_argument("item_id", help="Spotify item ID")
    parser.add_argument("-t", "--type", choices=["track", "album", "artist"],
                        required=True, help="Item type")
    parser.add_argument("--format", choices=["json", "text"], default="json",
                        help="Output format (default: json)")
    args = parser.parse_args()

    try:
        config = Config.load()
        if not config.spotify.is_configured():
            fail("Spotify credentials not configured",
                 hint="Run setup_config to set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET",
                 recoverable=False)

        service = SpotifyService(config.spotify)
        data = service.get_info(args.item_id, args.type)

        if args.format == "text":
            print(format_text(data, args.type))
        else:
            hint = f"{args.type.title()} info: {data['name']}"
            ok(data, hint=hint)
    except ValueError as e:
        fail(str(e), hint="Check your Spotify configuration", recoverable=False)
    except Exception as e:
        fail(str(e), hint="Spotify API request failed", recoverable=True)


if __name__ == "__main__":
    main()
