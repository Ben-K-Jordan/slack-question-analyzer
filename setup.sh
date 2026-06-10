#!/usr/bin/env bash
# Slack Question Analyzer — one-command setup for macOS and Linux.
#   ./setup.sh
set -euo pipefail
cd "$(dirname "$0")"

echo "=== Slack Question Analyzer setup ==="

# 1. Python
PYTHON=python3
if ! command -v "$PYTHON" >/dev/null 2>&1; then
    echo "ERROR: Python 3 is not installed. Install 3.10+ from https://python.org" >&2
    exit 1
fi
if ! "$PYTHON" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)'; then
    echo "ERROR: Python 3.10+ is required (found $("$PYTHON" -V))." >&2
    exit 1
fi
echo "[OK] $("$PYTHON" -V)"

# 2. Install the package
echo "Installing the analyzer (this can take a few minutes the first time)..."
"$PYTHON" -m pip install --quiet -e .
echo "[OK] Package installed"

# 3. Ollama
if ! command -v ollama >/dev/null 2>&1; then
    echo "Ollama is not installed. Install it with:" >&2
    echo "    curl -fsSL https://ollama.com/install.sh | sh     # Linux" >&2
    echo "    or download from https://ollama.com/download      # macOS" >&2
    echo "Then run this script again." >&2
    exit 1
fi
echo "[OK] Ollama installed"

# Make sure the Ollama server is running
if ! curl -s --max-time 3 http://localhost:11434/api/tags >/dev/null; then
    echo "Starting Ollama..."
    (ollama serve >/dev/null 2>&1 &)
    sleep 4
fi
echo "[OK] Ollama running"

# 4. Pull the models (idempotent; skips anything already downloaded)
echo "Downloading models (first time only: ~270MB + ~2GB)..."
ollama pull nomic-embed-text
ollama pull llama3.2
echo "[OK] Models ready"

# 5. Launch — the dashboard opens in your browser automatically
echo
echo "Starting the analyzer at http://localhost:5000 ..."
exec "$PYTHON" api_server.py
