#!/usr/bin/env python3
"""
Install MusicMaster dependencies.

Usage:
    python scripts/setup_env.py [--with-qobuz] [--with-tidal]

Creates virtual environment and installs required packages.
"""

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from lib.output import ok, fail


def get_skill_dir():
    return Path(__file__).parent.parent.absolute()


def get_venv_dir():
    return get_skill_dir() / ".venv"


def main():
    parser = argparse.ArgumentParser(description="Install MusicMaster dependencies")
    parser.add_argument("--with-qobuz", action="store_true", help="Install qobuz-dl")
    parser.add_argument("--with-tidal", action="store_true", help="Install tiddl")
    parser.add_argument("--force", action="store_true", help="Recreate venv if exists")
    args = parser.parse_args()

    venv_dir = get_venv_dir()
    skill_dir = get_skill_dir()

    # Handle existing venv
    if venv_dir.exists():
        if args.force:
            print("Removing existing venv...", file=sys.stderr)
            import shutil
            shutil.rmtree(venv_dir)
        else:
            print("Virtual environment already exists, reusing.", file=sys.stderr)

    # Create venv if needed
    if not venv_dir.exists():
        print("Creating virtual environment...", file=sys.stderr)
        try:
            subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)
        except subprocess.CalledProcessError as e:
            fail(f"Failed to create venv: {e}", hint="Ensure python3-venv is installed", recoverable=False)

    # Get pip path
    pip_path = venv_dir / "bin" / "pip"
    if sys.platform == "win32":
        pip_path = venv_dir / "Scripts" / "pip.exe"

    # Install core dependencies
    core_deps = ["spotipy", "pylast", "requests", "python-dotenv"]
    print(f"Installing core dependencies: {', '.join(core_deps)}", file=sys.stderr)
    try:
        subprocess.run([str(pip_path), "install", "-q"] + core_deps, check=True)
    except subprocess.CalledProcessError as e:
        fail(f"Failed to install core dependencies: {e}", hint="Check network connection and pip configuration", recoverable=True)

    # Optional: Qobuz
    if args.with_qobuz:
        print("Installing qobuz-dl...", file=sys.stderr)
        try:
            subprocess.run([str(pip_path), "install", "-q", "qobuz-dl"], check=True)
        except subprocess.CalledProcessError as e:
            fail(f"Failed to install qobuz-dl: {e}", hint="Try: pip install qobuz-dl manually", recoverable=True)

    # Optional: TIDAL (uses tiddl - modern alternative to tidal-dl)
    if args.with_tidal:
        print("Installing tiddl...", file=sys.stderr)
        try:
            subprocess.run([str(pip_path), "install", "-q", "tiddl"], check=True)
        except subprocess.CalledProcessError as e:
            fail(f"Failed to install tiddl: {e}", hint="Try: pip install tiddl manually", recoverable=True)

    # Create run helper scripts
    run_sh = skill_dir / "run.sh"
    with open(run_sh, 'w') as f:
        f.write(f'''#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/.venv/bin/activate"
cd "$SCRIPT_DIR"
python "scripts/$1.py" "${{@:2}}"
''')
    run_sh.chmod(0o755)

    run_bat = skill_dir / "run.bat"
    with open(run_bat, 'w') as f:
        f.write('''@echo off
set SCRIPT_DIR=%~dp0
call "%SCRIPT_DIR%.venv\\Scripts\\activate.bat"
cd /d "%SCRIPT_DIR%"
python "scripts\\%1.py" %*
''')

    ok({
        "status": "ok",
        "venv_path": str(venv_dir),
        "run_helper": str(run_sh)
    }, hint="Environment setup complete. Edit .env with your credentials.")


if __name__ == "__main__":
    main()
