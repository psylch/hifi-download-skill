#!/bin/bash
# MusicMaster setup script
# Usage: bash setup.sh check|install|preflight [--with-qobuz] [--with-tidal] [--force]

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$SKILL_DIR/.venv"

# ── JSON error helper ────────────────────────────────────────────────

json_error() {
    local msg="$1"
    local hint="${2:-}"
    local recoverable="${3:-true}"
    echo "{\"error\":\"$msg\",\"hint\":\"$hint\",\"recoverable\":$recoverable}" >&2
    if [ "$recoverable" = "true" ]; then
        exit 1
    else
        exit 2
    fi
}

# ── check subcommand (JSON output) ──────────────────────────────────

check() {
    local ready=true

    # Python
    local python_json
    if command -v python3 > /dev/null 2>&1; then
        local py_ver
        py_ver="$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")')"
        python_json="{\"ok\":true,\"version\":\"$py_ver\"}"
    else
        python_json='{"ok":false,"error":"python3 not found"}'
        ready=false
    fi

    # Venv
    local venv_json
    local deps_json='{}'
    if [ -d "$VENV_DIR" ]; then
        venv_json='{"ok":true}'
        PYTHON="$VENV_DIR/bin/python"

        # Check core deps
        local spotipy pylast requests dotenv
        spotipy=$($PYTHON -c "import spotipy" 2>/dev/null && echo true || echo false)
        pylast=$($PYTHON -c "import pylast" 2>/dev/null && echo true || echo false)
        requests=$($PYTHON -c "import requests" 2>/dev/null && echo true || echo false)
        dotenv=$($PYTHON -c "import dotenv" 2>/dev/null && echo true || echo false)
        deps_json="{\"spotipy\":$spotipy,\"pylast\":$pylast,\"requests\":$requests,\"dotenv\":$dotenv}"

        if [ "$spotipy" = "false" ] || [ "$pylast" = "false" ] || [ "$requests" = "false" ] || [ "$dotenv" = "false" ]; then
            ready=false
        fi

        # Check optional deps
        local qobuz_dl tiddl
        qobuz_dl=$($PYTHON -c "import qobuz_dl" 2>/dev/null && echo true || echo false)
        tiddl=$(command -v "$VENV_DIR/bin/tiddl" > /dev/null 2>&1 && echo true || echo false)
        deps_json="{\"spotipy\":$spotipy,\"pylast\":$pylast,\"requests\":$requests,\"dotenv\":$dotenv,\"qobuz_dl\":$qobuz_dl,\"tiddl\":$tiddl}"
    else
        venv_json='{"ok":false,"error":"not created"}'
        ready=false
    fi

    # Check .env
    local env_json
    if [ -f "$SKILL_DIR/.env" ]; then
        env_json='{"ok":true}'
    else
        env_json='{"ok":false,"error":"missing"}'
        ready=false
    fi

    local hint
    if [ "$ready" = "true" ]; then
        hint="All checks passed."
    else
        hint="Run: bash scripts/setup.sh install to set up dependencies."
    fi

    echo "{\"ready\":$ready,\"dependencies\":{\"python\":$python_json,\"venv\":$venv_json,\"packages\":$deps_json},\"credentials\":{\"env_file\":$env_json},\"hint\":\"$hint\"}"
}

install() {
    local with_qobuz=false
    local with_tidal=false
    local force=false

    for arg in "$@"; do
        case $arg in
            --with-qobuz) with_qobuz=true ;;
            --with-tidal) with_tidal=true ;;
            --force) force=true ;;
        esac
    done

    if ! command -v python3 &>/dev/null; then
        json_error "python3 not found" "Install Python 3.8+ first." "false"
    fi

    # Create venv
    if [ -d "$VENV_DIR" ] && [ "$force" = true ]; then
        echo "Removing existing venv..." >&2
        rm -rf "$VENV_DIR"
    fi

    if [ ! -d "$VENV_DIR" ]; then
        echo "Creating virtual environment..." >&2
        if ! python3 -m venv "$VENV_DIR"; then
            json_error "Failed to create virtual environment" "Check python3-venv is installed." "true"
        fi
    fi

    PIP="$VENV_DIR/bin/pip"

    # Core deps
    echo "Installing core dependencies..." >&2
    if ! $PIP install -q spotipy pylast requests python-dotenv; then
        json_error "pip install failed" "Check network connectivity and pip configuration." "true"
    fi

    # Optional deps
    if [ "$with_qobuz" = true ]; then
        echo "Installing qobuz-dl..." >&2
        $PIP install -q qobuz-dl
    fi
    if [ "$with_tidal" = true ]; then
        echo "Installing tiddl..." >&2
        $PIP install -q tiddl
    fi

    # Create .env from example if not exists
    if [ ! -f "$SKILL_DIR/.env" ] && [ -f "$SKILL_DIR/.env.example" ]; then
        cp "$SKILL_DIR/.env.example" "$SKILL_DIR/.env"
        echo "Created .env from template — edit with your credentials" >&2
    fi

    echo '{"status":"ok","hint":"Setup complete. Edit .env with your credentials if needed."}'
}

preflight() {
    # Output JSON to stdout for environment readiness check
    local ready=true

    # Python
    local py_json
    if command -v python3 &>/dev/null; then
        local py_ver
        py_ver="$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")')"
        py_json="{\"ok\":true,\"version\":\"$py_ver\"}"
    else
        py_json='{"ok":false,"error":"python3 not found"}'
        ready=false
        # Python missing is unrecoverable
        echo '{"error":"python3 not found","hint":"Install Python 3.8+ to use this skill.","recoverable":false}' >&2
        exit 2
    fi

    # Venv
    local venv_json
    if [ -d "$VENV_DIR" ]; then
        venv_json='{"ok":true}'
    else
        venv_json='{"ok":false,"error":"not created — run: bash scripts/setup.sh install"}'
        ready=false
    fi

    # Core dependencies (only check if venv exists)
    local deps_json='{}'
    if [ -d "$VENV_DIR" ]; then
        PYTHON="$VENV_DIR/bin/python"
        local spotipy pylast requests dotenv
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
    local cred_json
    if [ -f "$SKILL_DIR/.env" ]; then
        cred_json='{"env_file":true}'
    else
        cred_json='{"env_file":false}'
        ready=false
    fi

    local hint
    if [ "$ready" = "true" ]; then
        hint="All checks passed. Environment is ready."
    else
        hint="Some checks failed. Run: bash scripts/setup.sh install"
    fi

    echo "{\"ready\":$ready,\"dependencies\":{\"python\":$py_json,\"venv\":$venv_json,\"packages\":$deps_json},\"credentials\":$cred_json,\"hint\":\"$hint\"}"
}

case "${1:-check}" in
    check) check ;;
    install) shift; install "$@" ;;
    preflight) preflight ;;
    *)
        json_error "Unknown subcommand: ${1}" "Usage: bash setup.sh check|install|preflight [--with-qobuz] [--with-tidal] [--force]" "false"
        ;;
esac
