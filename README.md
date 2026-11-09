# repo-health

A lightweight, dependency-free Python command-line tool that checks a local repository for common maintenance and contribution-readiness files. It provides a quick checklist—not a security audit or a certification of project quality.

## What it checks

- **License** — common license file names such as `LICENSE`, `LICENSE.md`, `LICENSE.txt`, or `COPYING`
- **Contributing guide** — `CONTRIBUTING.md` in the repository root or `.github/`
- **Code of conduct** — `CODE_OF_CONDUCT.md` in the repository root or `.github/`
- **Security policy** — `SECURITY.md` in the repository root or `.github/`
- **GitHub Actions workflows** — at least one `.yml` or `.yaml` file in `.github/workflows/`
- **Dependency updates** — `.github/dependabot.yml` or `.github/dependabot.yaml`

Checks look for expected files and do not assess their contents. File and directory matching is case-insensitive.

## Requirements

- Python 3.10 or newer

## Install

From a clone of this repository, install the package:

```bash
python -m pip install .
```

For development, use an editable install:

```bash
python -m pip install -e .
```

## Use

Check the current directory:

```bash
repo-health .
```

Check another local repository:

```bash
repo-health /path/to/project
```

On Windows, if `repo-health` is not recognized, run it as a Python module:

```bat
python -m repo_health.cli .
```

You can also use a Windows path:

```bat
python -m repo_health.cli C:\path\to\project
```

If you prefer the `repo-health` command, add the Python `Scripts` directory reported by pip to your `PATH`, then open a new terminal.

### Output formats

Text output is the default. For machine-readable JSON:

```bash
repo-health . --format json
```

### Select checks

By default, all checks run. Use `--check` to run only selected checks, or `--skip` to omit checks. Both options can be repeated; use the check names exactly as listed below:

- `License`
- `Contributing guide`
- `Code of conduct`
- `Security policy`
- `GitHub Actions workflows`
- `Dependency updates`

For example, run only the license and security policy checks:

```bash
repo-health . --check License --check "Security policy"
```

Or skip the code of conduct check:

```bash
repo-health . --skip "Code of conduct"
```

### Exit status

The command returns status `1` if any selected check finds a missing item, and `0` if all selected checks pass. Use `--no-fail` to return success even when checks report missing items—for example, when introducing the tool into a CI workflow:

```bash
repo-health . --no-fail
```

Invalid paths or arguments return a nonzero status.

## Development

Run the test suite using Python's built-in `unittest` runner:

```bash
python -m unittest discover -s tests -v
```

If you have pytest installed, you can also run:

```bash
python -m pytest -q
```

Contributions and bug reports are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).
