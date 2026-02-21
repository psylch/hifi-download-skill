#!/usr/bin/env python3
"""Search for music on TIDAL or Qobuz."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from lib.config import Config
from lib.output import ok, fail
from lib.platform import get_platform_service


def format_text(result: dict) -> str:
    """Format search results as a numbered text list."""
    items = result.get("results", [])
    platform = result.get("platform", "").upper()
    search_type = result.get("search_type", "")
    query = result.get("query", "")

    if not items:
        return f"No {search_type}s found on {platform} for '{query}'"

    lines = [f"Found {len(items)} {platform} {search_type}(s) for '{query}':\n"]
    for idx, item in enumerate(items, 1):
        name = item.get("name", "Unknown")
        artists = item.get("artists", "")
        item_id = item.get("id") or item.get("qobuz_id", "")
        if artists:
            lines.append(f"{idx}. {name} by {artists} [ID: {item_id}]")
        else:
            lines.append(f"{idx}. {name} [ID: {item_id}]")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Search TIDAL or Qobuz for Hi-Res music")
    parser.add_argument("query", help="Search query")
    parser.add_argument("-p", "--platform", choices=["qobuz", "tidal"],
                        required=True, help="Platform to search")
    parser.add_argument("-t", "--type", choices=["track", "album", "artist"],
                        default="album", help="Search type (default: album)")
    parser.add_argument("-l", "--limit", type=int, default=10, help="Number of results (default: 10)")
    parser.add_argument("--format", choices=["json", "text"], default="json",
                        help="Output format (default: json)")
    args = parser.parse_args()

    try:
        config = Config.load()
    except Exception as e:
        fail(str(e), hint="Check your configuration", recoverable=False)

    if args.platform == "qobuz" and not config.qobuz.is_configured():
        fail("Qobuz not configured. Set QOBUZ_EMAIL and QOBUZ_PASSWORD.",
             hint="Configure Qobuz credentials in environment or config file",
             recoverable=False)

    try:
        service = get_platform_service(args.platform, config)
        result = service.search(args.query, args.type, args.limit)

        if args.format == "text":
            print(format_text(result))
        else:
            n = result.get("total", 0)
            ok(result, hint=f"Found {n} results on {args.platform}")

    except Exception as e:
        fail(str(e), hint=f"Search failed on {args.platform}")


if __name__ == "__main__":
    main()
