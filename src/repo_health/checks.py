"""Simple, local repository maintenance checks."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class Finding:
    name: str
    passed: bool
    message: str
    expected: str

    def to_dict(self) -> dict[str, str | bool]:
        return asdict(self)


def _find_case_insensitive(root: Path, candidate: str) -> Path | None:
    """Find a path beneath root, matching each path segment without case sensitivity."""
    current = root

    for segment in Path(candidate).parts:
        try:
            match = next(
                (
                    child
                    for child in current.iterdir()
                    if child.name.casefold() == segment.casefold()
                ),
                None,
            )
        except (FileNotFoundError, NotADirectoryError):
            return None

        if match is None:
            return None
        current = match

    return current


def _has_any_file(root: Path, candidates: tuple[str, ...]) -> bool:
    return any(
        (match := _find_case_insensitive(root, candidate)) is not None
        and match.is_file()
        for candidate in candidates
    )


def check_repository(root: Path) -> list[Finding]:
    """Return checks for common project metadata files beneath ``root``."""
    checks = [
        (
            "License",
            ("LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING"),
            "Add a LICENSE file that explains how others may use your project.",
        ),
        (
            "Contributing guide",
            ("CONTRIBUTING.md", ".github/CONTRIBUTING.md"),
            "Add CONTRIBUTING.md with setup, testing, and contribution instructions.",
        ),
        (
            "Code of conduct",
            ("CODE_OF_CONDUCT.md", ".github/CODE_OF_CONDUCT.md"),
            "Add a code of conduct to set expectations for community participation.",
        ),
        (
            "Security policy",
            ("SECURITY.md", ".github/SECURITY.md"),
            "Add SECURITY.md with instructions for reporting vulnerabilities.",
        ),
    ]

    findings = []
    for name, paths, suggestion in checks:
        passed = _has_any_file(root, paths)
        findings.append(
            Finding(
                name=name,
                passed=passed,
                message="Found an expected file." if passed else suggestion,
                expected=" or ".join(paths),
            )
        )

    workflows_dir = _find_case_insensitive(root, ".github/workflows")
    has_workflows = (
        workflows_dir is not None
        and workflows_dir.is_dir()
        and any(
            child.is_file() and child.suffix.casefold() in {".yml", ".yaml"}
            for child in workflows_dir.iterdir()
        )
    )
    findings.append(
        Finding(
            name="GitHub Actions workflows",
            passed=has_workflows,
            message=(
                "Found at least one workflow."
                if has_workflows
                else "Add a workflow under .github/workflows/ to automate tests or other project tasks."
            ),
            expected=".github/workflows/*.yml or .yaml",
        )
    )

    dependabot_paths = (".github/dependabot.yml", ".github/dependabot.yaml")
    has_dependabot = _has_any_file(root, dependabot_paths)
    findings.append(
        Finding(
            name="Dependency updates",
            passed=has_dependabot,
            message=(
                "Found Dependabot configuration."
                if has_dependabot
                else "Add .github/dependabot.yml to configure automated dependency update proposals."
            ),
            expected=" or ".join(dependabot_paths),
        )
    )

    return findings
