# repo-health

A lightweight, dependency-free Python CLI that checks a local repository for common maintenance and contribution-readiness gaps. It is intended as a helpful checklist, not a security audit or a certification of project quality.

## Requirements

- Python 3.10 or newer

## Install

From a clone of this repository:

```bash
python -m pip install .
```

For development, install the package in editable mode:

```bash
python -m pip install -e .
```

## Use

Check the current directory:

```bash
repo-health .
```

Or point it at another local checkout:

```bash
repo-health /path/to/project
```

Machine-readable output is available with `--format json`:

```bash
repo-health . --format json
```

The first version checks for a license, contribution guide, code of conduct, security policy, GitHub Actions workflows, and Dependabot configuration. Checks are intentionally simple and only look for expected files; they do not assess the quality or correctness of their contents.

The command exits with status `1` when it finds missing items, and `0` when all checks pass. Use `--no-fail` to always exit successfully, for example when initially adding the tool to a CI workflow. Invalid paths or arguments return a nonzero exit status.

## Development

Run the test suite with:

```bash
python -m unittest discover -s tests -v
```

Contributions and bug reports are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).
