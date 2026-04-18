#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# serve_api.sh  —  Start the FastAPI server
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "═══════════════════════════════════════════════"
echo "  PolyGuard API  —  http://localhost:8000"
echo "  Docs           —  http://localhost:8000/docs"
echo "═══════════════════════════════════════════════"

uvicorn src.inference.api:app --reload --host 0.0.0.0 --port 8000
