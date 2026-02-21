#!/usr/bin/env python3
"""Verify MusicMaster configuration and test connections."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from lib.config import Config
from lib.output import ok, fail


def check_spotify(config):
    """Check Spotify configuration."""
    if not config.spotify.is_configured():
        return False, "Not configured (missing SPOTIFY_CLIENT_ID or SPOTIFY_CLIENT_SECRET)"

    try:
        import spotipy
        from spotipy.oauth2 import SpotifyClientCredentials

        auth = SpotifyClientCredentials(
            client_id=config.spotify.client_id,
            client_secret=config.spotify.client_secret
        )
        sp = spotipy.Spotify(auth_manager=auth)
        # Test with a simple search
        sp.search("test", limit=1)
        return True, "Connected"
    except Exception as e:
        return False, f"Connection failed: {e}"


def check_lastfm(config):
    """Check Last.fm configuration."""
    if not config.lastfm.is_configured():
        return False, "Not configured (missing LASTFM_API_KEY)"

    try:
        import requests
        resp = requests.get(
            "http://ws.audioscrobbler.com/2.0/",
            params={
                "method": "artist.getSimilar",
                "artist": "Radiohead",
                "limit": 1,
                "api_key": config.lastfm.api_key,
                "format": "json"
            },
            timeout=10
        )
        data = resp.json()
        if "error" in data:
            return False, f"API error: {data.get('message')}"
        return True, "Connected"
    except Exception as e:
        return False, f"Connection failed: {e}"


def check_qobuz(config):
    """Check Qobuz configuration."""
    if not config.qobuz.is_configured():
        return False, "Not configured (missing QOBUZ_EMAIL or QOBUZ_PASSWORD)"

    try:
        from qobuz_dl.core import QobuzDL
        qobuz = QobuzDL(
            directory=config.qobuz.download_path,
            quality=config.qobuz.quality
        )
        qobuz.get_tokens()
        qobuz.initialize_client(
            config.qobuz.email,
            config.qobuz.password,
            qobuz.app_id,
            qobuz.secrets
        )
        return True, f"Connected (quality: {config.qobuz.quality})"
    except ImportError:
        return False, "qobuz-dl not installed (pip install qobuz-dl)"
    except Exception as e:
        return False, f"Login failed: {e}"


def check_tidal(config):
    """Check TIDAL configuration."""
    try:
        from TIDALDL.tidal import TidalAPI
        api = TidalAPI()
        if api.isLogin():
            return True, f"Connected (quality: {config.tidal.quality})"
        return False, "Not logged in. Run 'tidal-dl' to authenticate."
    except ImportError:
        return False, "tidal-dl not installed (pip install tidal-dl)"
    except Exception as e:
        return False, f"Error: {e}"


def format_human_readable(services_result, all_ok, required_ok):
    """Format verification results as human-readable text."""
    lines = ["MusicMaster Setup Verification", "", "=" * 50]

    for name, (is_ok, message) in services_result.items():
        icon = "+" if is_ok else "-"
        status = "OK" if is_ok else "FAIL"
        lines.append(f"[{icon}] {name}: {status}")
        lines.append(f"    {message}")

    lines.append("=" * 50)

    if all_ok:
        lines.append("")
        lines.append("All services configured and connected!")
    elif required_ok:
        lines.append("")
        lines.append("Required services (Spotify, Last.fm) are working.")
        lines.append("Download services (Qobuz/TIDAL) are optional.")
    else:
        lines.append("")
        lines.append("Required services not configured.")
        lines.append("Please configure Spotify and Last.fm to use MusicMaster.")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Verify MusicMaster configuration")
    parser.add_argument("--format", choices=["json", "text"], default="json",
                        help="Output format (default: json)")
    args = parser.parse_args()

    config = Config.load()

    # Check each service
    checkers = {
        "Spotify": check_spotify,
        "Last.fm": check_lastfm,
        "Qobuz": check_qobuz,
        "TIDAL": check_tidal,
    }

    all_ok = True
    required_ok = True
    services_result = {}

    for name, checker in checkers.items():
        is_ok, message = checker(config)
        services_result[name] = (is_ok, message)

        if not is_ok:
            all_ok = False
            if name in ["Spotify", "Last.fm"]:
                required_ok = False

    if args.format == "text":
        print(format_human_readable(services_result, all_ok, required_ok))
        if not required_ok:
            sys.exit(1)
        return

    # JSON output
    name_to_key = {"Spotify": "spotify", "Last.fm": "lastfm", "Qobuz": "qobuz", "TIDAL": "tidal"}
    services_json = {}
    for name, (is_ok, message) in services_result.items():
        key = name_to_key.get(name, name.lower())
        services_json[key] = {"ok": is_ok, "message": message}

    result = {
        "services": services_json,
        "all_ok": all_ok,
        "required_ok": required_ok
    }

    if not required_ok:
        fail(
            "Required services not configured",
            hint="Configure Spotify and Last.fm first",
            recoverable=True
        )
    else:
        hint = "All services working." if all_ok else "Required services (Spotify, Last.fm) working. Download services need setup."
        ok(result, hint=hint)


if __name__ == "__main__":
    main()
