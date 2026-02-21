#!/usr/bin/env python3
"""Get user's top tracks or artists from Spotify."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from lib.config import Config
from lib.output import ok, fail
from lib.spotify import SpotifyService


def format_text(data: dict) -> str:
    """Format user data as human-readable text."""
    results = data["results"]
    if not results:
        return f"No top {data['data_type']} found"

    lines = [f"Your top {data['total']} {data['data_type']} from {data['time_desc']}:\n"]
    for idx, item in enumerate(results, 1):
        if data["data_type"] == "tracks":
            lines.append(f"{idx}. {item['name']} by {item['artists']} (ID: {item['id']})")
        elif data["data_type"] == "artists":
            lines.append(f"{idx}. {item['name']} (ID: {item['id']})")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Get your Spotify listening history")
    parser.add_argument("data_type", choices=["tracks", "artists"],
                        help="Type of data to retrieve")
    parser.add_argument("-r", "--range", dest="time_range",
                        choices=["short_term", "medium_term", "long_term"],
                        default="medium_term",
                        help="Time range: short_term (~4 weeks), medium_term (~6 months), long_term (years)")
    parser.add_argument("-l", "--limit", type=int, default=20, help="Number of results (default: 20)")
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
        data = service.get_user_data(args.data_type, args.time_range, args.limit)

        if args.format == "text":
            print(format_text(data))
        else:
            hint = f"Your top {data['total']} {data['data_type']} from {data['time_desc']}"
            ok(data, hint=hint)
    except ValueError as e:
        fail(str(e), hint="Check your Spotify configuration", recoverable=False)
    except Exception as e:
        fail(str(e), hint="Spotify API request failed", recoverable=True)


if __name__ == "__main__":
    main()
