"""Command-line interface for repo-health."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from repo_health.checks import Finding, check_repository


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="repo-health",
        description="Check a local repository for common maintenance files.",
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        type=Path,
        help="repository directory to inspect (default: current directory)",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="output format (default: text)",
    )
    parser.add_argument(
        "--no-fail",
        action="store_true",
        help="exit successfully even when checks find missing files",
    )
    return parser


def _text_report(path: Path, findings: list[Finding]) -> str:
    passed = sum(finding.passed for finding in findings)
    lines = [f"repo-health: {path}"]
    for finding in findings:
        marker = "PASS" if finding.passed else "WARN"
        lines.append(f"[{marker}] {finding.name}: {finding.message}")
    lines.append(f"\n{passed}/{len(findings)} checks passed")
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    path = args.path.expanduser().resolve()
    if not path.exists():
        parser.error(f"path does not exist: {path}")
    if not path.is_dir():
        parser.error(f"path is not a directory: {path}")

    findings = check_repository(path)
    if args.format == "json":
        print(
            json.dumps(
                {
                    "path": str(path),
                    "passed": sum(item.passed for item in findings),
                    "total": len(findings),
                    "findings": [item.to_dict() for item in findings],
                },
                indent=2,
            )
        )
    else:
        print(_text_report(path, findings))

    has_warnings = any(not finding.passed for finding in findings)
    return 1 if has_warnings and not args.no_fail else 0


if __name__ == "__main__":
    sys.exit(main())
