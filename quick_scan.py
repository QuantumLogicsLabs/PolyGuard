#!/usr/bin/env python3
"""
quick_scan.py
=============
Convenience CLI to scan a file or inline code snippet without bash.

Examples
--------
# Scan a file (rules-only, no model needed):
    python quick_scan.py --file path/to/code.py

# Scan inline code:
    python quick_scan.py --code 'cursor.execute("SELECT * FROM t WHERE id=" + uid)' --language python

# Use the trained ML model (requires models_saved/best_model.pt):
    python quick_scan.py --file path/to/code.js --language javascript --use-model
"""
import argparse
import sys
from src.inference.pipeline import PolyGuardPipeline

SEVERITY_COLOR = {
    "Critical": "\033[91m",   # red
    "High":     "\033[93m",   # yellow
    "Medium":   "\033[94m",   # blue
    "Low":      "\033[96m",   # cyan
}
RESET = "\033[0m"
BOLD  = "\033[1m"


def colorize(text: str, severity: str) -> str:
    return f"{SEVERITY_COLOR.get(severity, '')}{text}{RESET}"


def main():
    parser = argparse.ArgumentParser(description="PolyGuard — Quick Code Scanner")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--file",  help="Path to source file to scan")
    group.add_argument("--code",  help="Inline code snippet to scan")
    parser.add_argument("--language", default="python",
                        choices=["python", "javascript", "cpp", "c", "typescript"],
                        help="Programming language (default: python)")
    parser.add_argument("--use-model", action="store_true",
                        help="Load trained ML model (requires models_saved/best_model.pt)")
    parser.add_argument("--threshold", type=float, default=0.5,
                        help="ML confidence threshold (default: 0.5)")
    args = parser.parse_args()

    # ── Load code ─────────────────────────────────────────────────────────────
    if args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                code = f.read()
            source_label = args.file
        except FileNotFoundError:
            print(f"Error: File not found: {args.file}", file=sys.stderr)
            sys.exit(1)
    else:
        code = args.code
        source_label = "<inline>"

    # ── Build pipeline ────────────────────────────────────────────────────────
    if args.use_model:
        pipeline = PolyGuardPipeline.from_pretrained(
            "models_saved/best_model.pt", threshold=args.threshold
        )
    else:
        pipeline = PolyGuardPipeline.rules_only()

    # ── Scan ──────────────────────────────────────────────────────────────────
    result = pipeline.analyze(code, language=args.language)

    # ── Output ────────────────────────────────────────────────────────────────
    print(f"\n{BOLD}{'═'*58}{RESET}")
    print(f"{BOLD}  PolyGuard Security Scan{RESET}")
    print(f"  Source   : {source_label}")
    print(f"  Language : {args.language}")
    print(f"  Risk     : {colorize(result.overall_risk, result.overall_risk)}")
    print(f"  Time     : {result.scan_time_ms:.1f} ms")
    print(f"{BOLD}{'═'*58}{RESET}\n")

    if not result.findings:
        print("  ✅  No vulnerabilities detected.\n")
        sys.exit(0)

    for i, f in enumerate(result.findings, 1):
        sev_str = colorize(f"[{f.severity}]", f.severity)
        print(f"  {BOLD}[{i}]{RESET} {sev_str} {BOLD}{f.vuln_type.upper()}{RESET}"
              f"  —  Line {f.line}  (confidence: {f.confidence:.0%})  [{f.source}]")
        print(f"       {f.message}")
        if f.cwe:
            print(f"       {BOLD}CWE:{RESET} {f.cwe}")
        if f.suggested_fix:
            print(f"       {BOLD}Fix:{RESET} {f.suggested_fix}")
        print()

    sys.exit(1 if result.overall_risk in ("Critical", "High") else 0)


if __name__ == "__main__":
    main()
