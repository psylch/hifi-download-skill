#!/usr/bin/env python3
"""Search for music on Spotify."""

import argparse
import sys
from pathlib import Path

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent))

from lib.config import Config
from lib.output import ok, fail
from lib.spotify import SpotifyService


def format_text(data: dict) -> str:
    """Format search results as human-readable text."""
    results = data["results"]
    if not results:
        return f"No {data['search_type']}s found for '{data['query']}'"

    lines = [f"Found {data['total']} {data['search_type']}(s) for '{data['query']}':\n"]
    for idx, item in enumerate(results, 1):
        if data["search_type"] == "track":
            lines.append(f"{idx}. {item['name']} by {item['artists']} (ID: {item['id']})")
        elif data["search_type"] == "album":
            lines.append(f"{idx}. {item['name']} by {item['artists']} (ID: {item['id']})")
        elif data["search_type"] == "artist":
            lines.append(f"{idx}. {item['name']} (ID: {item['id']})")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Search Spotify for music")
    parser.add_argument("query", help="Search query")
    parser.add_argument("-t", "--type", choices=["track", "album", "artist", "playlist"],
                        default="track", help="Search type (default: track)")
    parser.add_argument("-l", "--limit", type=int, default=10, help="Number of results (default: 10)")
    parser.add_argument("-m", "--market", default="US", help="Market code (default: US)")
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
        data = service.search(args.query, args.type, args.limit, args.market)

        if args.format == "text":
            print(format_text(data))
        else:
            hint = f"Found {data['total']} {data['search_type']}(s) matching '{data['query']}'"
            ok(data, hint=hint)
    except ValueError as e:
        fail(str(e), hint="Check your Spotify configuration", recoverable=False)
    except Exception as e:
        fail(str(e), hint="Spotify API request failed", recoverable=True)


if __name__ == "__main__":
    main()
