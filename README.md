# hifi-download-skill

[中文文档](README.zh.md)

A [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skill for music discovery and high-quality audio downloads. Combines Spotify and Last.fm for discovery with Qobuz and TIDAL for lossless audio downloads.

| Step | What Happens | Service Used |
|------|-------------|--------------|
| **Discover** | Search music, find similar artists/tracks | Spotify, Last.fm |
| **Recommend** | Personalized recommendations from listening history | Spotify + Last.fm |
| **Search** | Find albums/tracks on download platforms | Qobuz, TIDAL |
| **Download** | Download in lossless quality (FLAC/Hi-Res) | Qobuz, TIDAL |

## Installation

### Install all media skills at once (recommended)

This skill is part of [media-master](https://github.com/psylch/media-master), which bundles music, cloud drive, and book download skills:

```bash
npx skills add psylch/media-master -g -y
```

### Install this skill only

```bash
npx skills add psylch/hifi-download-skill -g -y
```

### Via Claude Code Plugin Marketplace

```shell
/plugin marketplace add psylch/hifi-download-skill
/plugin install hifi-download@psylch-hifi-download-skill
```

Restart Claude Code after installation.

## Prerequisites

- **Python 3** installed
- **API credentials** for at least one discovery service:
  - Spotify: Free account + API credentials ([developer.spotify.com](https://developer.spotify.com/dashboard))
  - Last.fm: Free API key ([last.fm/api](https://www.last.fm/api/account/create))
- **Subscription** for download services (optional):
  - Qobuz: Studio or Sublime subscription
  - TIDAL: HiFi+ subscription

## Usage

In Claude Code, use any of these trigger phrases:

```
find music like Radiohead
recommend songs based on my taste
download album OK Computer in Hi-Res
search for FLAC albums
setup music services
```

## How It Works

1. **Setup** — installs dependencies, configures API credentials
2. **Status check** — verifies which services are available
3. **Discovery** — searches Spotify, finds similar artists/tracks via Last.fm
4. **Recommendations** — combines Spotify listening history with Last.fm data
5. **Download** — searches Qobuz/TIDAL catalog, downloads in configured quality

## Supported Services

| Service | Type | Requirements |
|---------|------|--------------|
| Spotify | Discovery | Free account + API credentials |
| Last.fm | Discovery | Free API key |
| Qobuz | Downloads | Studio/Sublime subscription |
| TIDAL | Downloads | HiFi+ subscription |

## File Structure

```
hifi-download-skill/
├── .claude-plugin/
│   ├── marketplace.json
│   └── plugin.json
├── skills/
│   └── hifi-download/
│       ├── SKILL.md              # Main skill definition
│       ├── run.sh                # Venv-aware script runner
│       ├── .env.example          # Credential template
│       ├── references/
│       │   ├── setup_guide.md    # Detailed setup instructions
│       │   └── musicmaster.md    # Complete script reference
│       └── scripts/
│           ├── setup.sh          # Environment setup
│           ├── setup_config.py   # Credential configuration
│           ├── status.py         # Service status check
│           ├── spotify_*.py      # Spotify scripts
│           ├── lastfm_*.py       # Last.fm scripts
│           ├── platform_*.py     # Qobuz/TIDAL scripts
│           └── lib/              # Shared modules
├── README.md
└── LICENSE
```

## Acknowledgments

This project relies on the following open-source tools:

- **[tiddl](https://github.com/oskvr37/tiddl)** - TIDAL downloader by [@oskvr37](https://github.com/oskvr37)
- **[qobuz-dl](https://github.com/vitiko98/qobuz-dl)** - Qobuz downloader by [@vitiko98](https://github.com/vitiko98)

## Disclaimer

This tool is intended for **personal use only** and was created for educational purposes.

- This project is **not affiliated with** TIDAL, Qobuz, Spotify, or Last.fm
- Users must ensure their use complies with the respective services' terms of use and local copyright laws
- Downloaded content is for personal use and may not be shared or redistributed
- The developer assumes **no responsibility** for any misuse of this tool

By using this software, you agree to these terms.

## License

MIT
