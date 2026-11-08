"""Tests for repository health checks and the command-line interface."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from repo_health.checks import check_repository
from repo_health.cli import main


class CheckRepositoryTests(unittest.TestCase):
    def test_reports_missing_files(self):
        with tempfile.TemporaryDirectory() as directory:
            findings = check_repository(Path(directory))
        self.assertEqual(len(findings), 6)
        self.assertTrue(all(not finding.passed for finding in findings))

    def test_recognizes_supported_file_locations(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".github").mkdir()
            (root / ".github" / "CONTRIBUTING.md").write_text("How to contribute")
            (root / ".github" / "SECURITY.md").write_text("Report vulnerabilities")
            (root / "LICENSE.txt").write_text("License text")
            (root / ".github" / "dependabot.yaml").write_text("version: 2")
            workflows = root / ".github" / "workflows"
            workflows.mkdir()
            (workflows / "tests.YAML").write_text("name: tests")

            findings = {finding.name: finding for finding in check_repository(root)}

        self.assertTrue(findings["License"].passed)
        self.assertTrue(findings["Contributing guide"].passed)
        self.assertTrue(findings["Security policy"].passed)
        self.assertTrue(findings["Dependency updates"].passed)
        self.assertTrue(findings["GitHub Actions workflows"].passed)
        self.assertFalse(findings["Code of conduct"].passed)

    def test_cli_json_output_and_failure_status(self):
        with tempfile.TemporaryDirectory() as directory, patch("sys.stdout") as stdout:
            status = main([directory, "--format", "json"])
            report = json.loads("".join(call.args[0] for call in stdout.write.call_args_list))
        self.assertEqual(status, 1)
        self.assertEqual(report["total"], 6)
        self.assertEqual(len(report["findings"]), 6)

    def test_no_fail_keeps_success_status(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(main([directory, "--no-fail"]), 0)


if __name__ == "__main__":
    unittest.main()
