#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# run_tests.sh  —  Run the full test suite (excludes slow GPU tests)
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "═══════════════════════════════════════════════"
echo "  PolyGuard — Test Suite"
echo "═══════════════════════════════════════════════"

pytest tests/ -v -m "not slow" --tb=short

echo ""
echo "✅  Tests complete."
