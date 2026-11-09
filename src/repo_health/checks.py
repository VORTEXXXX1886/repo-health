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


def _find_case_insensitive_child(parent: Path, name: str) -> Path | None:
    """Return a child path whose name matches ``name`` ignoring case."""
    if not parent.exists():
        return None
    for child in parent.iterdir():
        if child.name.lower() == name.lower():
            return child
    return None


def _has_any_file(root: Path, candidates: tuple[str, ...]) -> bool:
    """Check whether any candidate relative path exists, ignoring filename case."""
    for candidate in candidates:
        path = Path(candidate)
        current = root
        matches = True
        for part in path.parts:
            next_path = _find_case_insensitive_child(current, part)
            if next_path is None:
                matches = False
                break
            current = next_path
        if matches and current.is_file():
            return True
    return False


def check_repository(root: Path) -> list[Finding]:
    """Return checks for common project metadata files beneath ``root``."""
    checks = [
        ("License", ("LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING"), "Add a LICENSE file that explains how others may use your project."),
        ("Contributing guide", ("CONTRIBUTING.md", ".github/CONTRIBUTING.md"), "Add CONTRIBUTING.md with setup, testing, and contribution instructions."),
        ("Code of conduct", ("CODE_OF_CONDUCT.md", ".github/CODE_OF_CONDUCT.md"), "Add a code of conduct to set expectations for community participation."),
        ("Security policy", ("SECURITY.md", ".github/SECURITY.md"), "Add SECURITY.md with instructions for reporting vulnerabilities."),
    ]
    findings = [
        Finding(
            name=name,
            passed=_has_any_file(root, paths),
            message=("Found an expected file." if _has_any_file(root, paths) else suggestion),
            expected=" or ".join(paths),
        )
        for name, paths, suggestion in checks
    ]

    github_dir = _find_case_insensitive_child(root, ".github")
    workflows_dir = None if github_dir is None else _find_case_insensitive_child(github_dir, "workflows")
    has_workflows = workflows_dir is not None and workflows_dir.is_dir() and any(
        child.is_file() and child.suffix.lower() in {".yml", ".yaml"}
        for child in workflows_dir.iterdir()
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
