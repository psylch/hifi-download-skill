#!/usr/bin/env python3
"""Find similar artists using Last.fm."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from lib.config import Config
from lib.lastfm import LastfmService
from lib.output import ok, fail


def format_text(data: dict) -> str:
    """Format similar artists dict as human-readable text."""
    lines = [f"Artists similar to '{data['query_artist']}':\n"]
    for idx, a in enumerate(data["results"], 1):
        line = f"{idx}. {a['name']} (similarity: {a['similarity']}%)"
        lines.append(line)
        if a.get("mbid"):
            lines.append(f"   MBID: {a['mbid']}")
        if a.get("url"):
            lines.append(f"   URL: {a['url']}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Find artists similar to a given artist")
    parser.add_argument("artist", help="Artist name")
    parser.add_argument("-l", "--limit", type=int, default=10, help="Number of results (default: 10)")
    parser.add_argument("--format", choices=["json", "text"], default="json", help="Output format (default: json)")
    args = parser.parse_args()

    config = Config.load()
    if not config.lastfm.is_configured():
        fail("Last.fm API key not configured", hint="Run setup_config.py with --lastfm-key=KEY", recoverable=False)

    try:
        service = LastfmService(config.lastfm.api_key)
        result = service.get_similar_artists(args.artist, args.limit)
    except ValueError as e:
        fail(str(e), hint="Check your Last.fm API key or try a different artist name")

    if args.format == "text":
        print(format_text(result))
    else:
        ok(result, hint=f"Found {result['total']} artists similar to '{args.artist}'")


if __name__ == "__main__":
    main()
