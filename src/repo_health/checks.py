"""Simple, local repository maintenance checks."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


CHECK_NAMES = (
    "License",
    "Contributing guide",
    "Code of conduct",
    "Security policy",
    "GitHub Actions workflows",
    "Dependency updates",
)


@dataclass(frozen=True)
class Finding:
    name: str
    passed: bool
    message: str
    expected: str

    def to_dict(self) -> dict[str, str | bool]:
        return asdict(self)


def _find_case_insensitive(root: Path, candidate: str) -> Path | None:
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


def _filter_checks(
    checks: Iterable[tuple[str, tuple[str, ...], str]],
    include: Iterable[str] | None = None,
    exclude: Iterable[str] | None = None,
) -> list[tuple[str, tuple[str, ...], str]]:
    include_set = set(include) if include else None
    exclude_set = set(exclude) if exclude else None

    filtered: list[tuple[str, tuple[str, ...], str]] = []
    for name, paths, suggestion in checks:
        if include_set is not None and name not in include_set:
            continue
        if exclude_set is not None and name in exclude_set:
            continue
        filtered.append((name, paths, suggestion))
    return filtered


def check_repository(
    root: Path,
    include: Iterable[str] | None = None,
    exclude: Iterable[str] | None = None,
) -> list[Finding]:
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

    all_checks = [
        *checks,
        (
            "GitHub Actions workflows",
            (),
            "Add a workflow under .github/workflows/ to automate tests or other project tasks.",
        ),
        (
            "Dependency updates",
            (),
            "Add .github/dependabot.yml to configure automated dependency update proposals.",
        ),
    ]

    filtered_checks = _filter_checks(all_checks, include=include, exclude=exclude)

    findings: list[Finding] = []
    for name, paths, suggestion in filtered_checks:
        if name in {"GitHub Actions workflows", "Dependency updates"}:
            if name == "GitHub Actions workflows":
                workflows_dir = _find_case_insensitive(root, ".github/workflows")
                passed = (
                    workflows_dir is not None
                    and workflows_dir.is_dir()
                    and any(
                        child.is_file() and child.suffix.casefold() in {".yml", ".yaml"}
                        for child in workflows_dir.iterdir()
                    )
                )
                expected = ".github/workflows/*.yml or .yaml"
                message = (
                    "Found at least one workflow."
                    if passed
                    else "Add a workflow under .github/workflows/ to automate tests or other project tasks."
                )
            else:
                dependabot_paths = (".github/dependabot.yml", ".github/dependabot.yaml")
                passed = _has_any_file(root, dependabot_paths)
                expected = " or ".join(dependabot_paths)
                message = (
                    "Found Dependabot configuration."
                    if passed
                    else "Add .github/dependabot.yml to configure automated dependency update proposals."
                )
        else:
            passed = _has_any_file(root, paths)
            expected = " or ".join(paths)
            message = "Found an expected file." if passed else suggestion

        findings.append(
            Finding(
                name=name,
                passed=passed,
                message=message,
                expected=expected,
            )
        )

    return findings
