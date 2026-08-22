# Contributing to mif-core

`mif-core` is the metric and strategy qualification layer of MIF. Contributions
must preserve the boundaries documented in `docs/ARCHITECTURE.md`.

## Local checks

```bash
python -m pip install -e '.[dev]'
python -m pytest
python -m ruff check core tests
python -m build
```

Tests must be deterministic and offline by default. A new test should answer
one precise question and expose its value, pass/fail result, and details.

Do not add network calls, implicit data cleaning, or hidden certification
criteria to the core package.

## Release path

Releases are published only from a GitHub Release through the protected
`publish.yml` workflow. Configure PyPI Trusted Publishing for the repository
before creating the first release; do not add a long-lived PyPI token to the
repository.
