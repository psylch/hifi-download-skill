#!/usr/bin/env python3
"""Find similar tracks using Last.fm."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from lib.config import Config
from lib.lastfm import LastfmService
from lib.output import ok, fail


def format_text(data: dict) -> str:
    """Format similar tracks dict as human-readable text."""
    lines = [f"Tracks similar to '{data['query_track']}' by {data['query_artist']}:\n"]
    for idx, t in enumerate(data["results"], 1):
        line = f"{idx}. {t['name']} by {t['artist']} (similarity: {t['similarity']}%)"
        lines.append(line)
        if t.get("duration"):
            lines.append(f"   Duration: {t['duration']}")
        if t.get("url"):
            lines.append(f"   URL: {t['url']}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Find tracks similar to a given track")
    parser.add_argument("track", help="Track name")
    parser.add_argument("artist", help="Artist name")
    parser.add_argument("-l", "--limit", type=int, default=10, help="Number of results (default: 10)")
    parser.add_argument("--format", choices=["json", "text"], default="json", help="Output format (default: json)")
    args = parser.parse_args()

    config = Config.load()
    if not config.lastfm.is_configured():
        fail("Last.fm API key not configured", hint="Run setup_config.py with --lastfm-key=KEY", recoverable=False)

    try:
        service = LastfmService(config.lastfm.api_key)
        result = service.get_similar_tracks(args.track, args.artist, args.limit)
    except ValueError as e:
        fail(str(e), hint="Check your Last.fm API key or try a different track/artist")

    if args.format == "text":
        print(format_text(result))
    else:
        ok(result, hint=f"Found {result['total']} tracks similar to '{args.track}' by {args.artist}")


if __name__ == "__main__":
    main()
