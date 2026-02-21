#!/usr/bin/env python3
"""
Re-enable a previously disabled service.

Usage:
    python scripts/enable_service.py spotify
    python scripts/enable_service.py tidal

This reverses the effect of disable_service.py.
Note: You still need to configure the service credentials.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from lib.config import Config
from lib.output import ok, fail
from lib.preferences import Preferences


VALID_SERVICES = ['spotify', 'lastfm', 'qobuz', 'tidal']


def main():
    parser = argparse.ArgumentParser(
        description="Re-enable a MusicMaster service",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/enable_service.py spotify
  python scripts/enable_service.py tidal

After enabling, you may still need to configure credentials
using setup_config.py if not already done.
"""
    )

    parser.add_argument("service", choices=VALID_SERVICES,
                        help="Service to enable")

    args = parser.parse_args()

    prefs = Preferences.load()
    config = Config.load()

    prefs.enable_service(args.service)

    # Check if configuration is needed
    needs_config = False
    config_hint = ""
    if args.service == "spotify" and not config.spotify.is_configured():
        needs_config = True
        config_hint = "Run setup_config.py with --spotify-id=... --spotify-secret=..."
    elif args.service == "lastfm" and not config.lastfm.is_configured():
        needs_config = True
        config_hint = "Run setup_config.py with --lastfm-key=..."
    elif args.service == "qobuz" and not config.qobuz.is_configured():
        needs_config = True
        config_hint = "Run setup_config.py with --qobuz-email=... --qobuz-password=..."
    elif args.service == "tidal":
        tiddl_config = Path.home() / "tiddl.json"
        if not tiddl_config.exists():
            needs_config = True
            config_hint = "Run tidal_auth.py to authorize TIDAL"

    result = {"service": args.service, "status": "enabled"}
    if needs_config:
        result["needs_config"] = True
        result["config_hint"] = config_hint

    ok(result, hint=f"Enabled {args.service}. {'Credentials still needed.' if needs_config else 'Ready to use.'}")


if __name__ == "__main__":
    main()
