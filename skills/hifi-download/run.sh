#!/bin/bash
# MusicMaster script runner — activates venv and runs the specified script
# Usage: bash run.sh <script_name> [args...]
# Example: bash run.sh status --json
# Example: bash run.sh preflight

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

# ── preflight: check environment readiness without requiring venv ─────
if [ "$1" = "preflight" ]; then
    ready=true

    # Python
    if command -v python3 &>/dev/null; then
        py_ver="$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")')"
        py_json="{\"ok\":true,\"version\":\"$py_ver\"}"
    else
        py_json='{"ok":false,"error":"python3 not found"}'
        ready=false
        # Python missing entirely is unrecoverable
        echo '{"error":"python3 not found","hint":"Install Python 3.8+ to use this skill.","recoverable":false}' >&2
        exit 2
    fi

    # Venv
    if [ -d "$VENV_DIR" ]; then
        venv_json='{"ok":true}'
    else
        venv_json='{"ok":false,"error":"not created — run: bash scripts/setup.sh install"}'
        ready=false
    fi

    # Core dependencies (only check if venv exists)
    deps_json='{}'
    if [ -d "$VENV_DIR" ]; then
        PYTHON="$VENV_DIR/bin/python"
        spotipy=$($PYTHON -c "import spotipy" 2>/dev/null && echo true || echo false)
        pylast=$($PYTHON -c "import pylast" 2>/dev/null && echo true || echo false)
        requests=$($PYTHON -c "import requests" 2>/dev/null && echo true || echo false)
        dotenv=$($PYTHON -c "import dotenv" 2>/dev/null && echo true || echo false)
        deps_json="{\"spotipy\":$spotipy,\"pylast\":$pylast,\"requests\":$requests,\"dotenv\":$dotenv}"
        if [ "$spotipy" = "false" ] || [ "$pylast" = "false" ] || [ "$requests" = "false" ] || [ "$dotenv" = "false" ]; then
            ready=false
        fi
    fi

    # Credentials (.env file)
    if [ -f "$SCRIPT_DIR/.env" ]; then
        cred_json='{"env_file":true}'
    else
        cred_json='{"env_file":false}'
        ready=false
    fi

    hint=""
    if [ "$ready" = "true" ]; then
        hint="All checks passed. Environment is ready."
    else
        hint="Some checks failed. Run: bash scripts/setup.sh install"
    fi
    echo "{\"ready\":$ready,\"dependencies\":{\"python\":$py_json,\"venv\":$venv_json,\"packages\":$deps_json},\"credentials\":$cred_json,\"hint\":\"$hint\"}"
    exit 0
fi

# ── normal script dispatch ────────────────────────────────────────────
if [ ! -d "$VENV_DIR" ]; then
    echo '{"error":"Virtual environment not found.","hint":"Run: bash scripts/setup.sh install","recoverable":true}' >&2
    exit 1
fi

source "$VENV_DIR/bin/activate"
cd "$SCRIPT_DIR"
python "scripts/$1.py" "${@:2}"
