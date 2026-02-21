#!/usr/bin/env python3
"""
Complete Spotify OAuth authorization.

Usage:
    python scripts/spotify_auth.py [--no-browser]

Opens browser for Spotify login. After authorization, prints user info as JSON.
Use --no-browser to only print the authorization URL.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from lib.config import Config
from lib.output import ok, fail


def main():
    parser = argparse.ArgumentParser(description="Complete Spotify OAuth authorization")
    parser.add_argument("--no-browser", action="store_true",
                        help="Don't open browser, just print authorization URL")
    args = parser.parse_args()

    try:
        config = Config.load()

        if not config.spotify.is_configured():
            fail("Spotify credentials not configured",
                 hint="Run setup_config to set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET",
                 recoverable=False)

        import spotipy
        from spotipy.oauth2 import SpotifyOAuth

        auth = SpotifyOAuth(
            client_id=config.spotify.client_id,
            client_secret=config.spotify.client_secret,
            redirect_uri=config.spotify.redirect_uri,
            scope="user-library-read user-top-read",
            open_browser=not args.no_browser
        )

        auth_url = auth.get_authorize_url()

        if args.no_browser:
            ok({
                "status": "pending",
                "auth_url": auth_url,
            }, hint="Open the auth_url in a browser to authorize, then run spotify_auth again")
            return

        print("Opening browser for Spotify authorization...", file=sys.stderr)
        print("Please log in and authorize the app.", file=sys.stderr)

        try:
            sp = spotipy.Spotify(auth_manager=auth)
            user = sp.current_user()

            ok({
                "status": "ok",
                "user": user["display_name"],
                "user_id": user["id"],
            }, hint="Spotify OAuth 授权成功，token 已缓存")

        except spotipy.SpotifyException as e:
            fail(f"Spotify API error: {e}",
                 hint="Authorization failed, please try again",
                 recoverable=True)

    except ImportError:
        fail("spotipy not installed",
             hint="Run setup_env to install dependencies",
             recoverable=False)
    except Exception as e:
        fail(str(e), recoverable=True)


if __name__ == "__main__":
    main()
