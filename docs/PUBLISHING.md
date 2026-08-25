# Publishing `mif-foundation`

The repository is `symbioticode/mif-core`, while the PyPI distribution is
`mif-foundation`. The import package remains `core` and the optional
CLI remains `mif-core`.

The current package metadata supports Python 3.11 and 3.12. Do not advertise a
Python 3.13 release until the `mif-dal`/NumPy compatibility constraint is
resolved.

## One-time PyPI setup

1. Create the PyPI project configuration for `mif-foundation`.
2. Add a Trusted Publisher using:
   - owner: `symbioticode`;
   - repository: `mif-core`;
   - workflow: `.github/workflows/publish.yml`;
   - environment: empty, unless a PyPI environment is deliberately chosen.
3. Do not add a PyPI API token to GitHub secrets. The workflow requests an
   OIDC identity token and uses Trusted Publishing.

## Release checklist

Before publishing a release, start from a clean checkout and a new virtual
environment using a supported Python version (3.11 or 3.12), then run:

```bash
python -m venv .venv-release
. .venv-release/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
python -m pytest --cov=core --cov-report=term-missing --cov-fail-under=90
python -m ruff check core tests examples
python -m ruff format --check core tests examples
python -m mypy core tests examples
python -m build
```

Check that the worktree is still clean, that both artifacts in `dist/` are
named `mif_foundation-<version>.*`, and that their metadata contains the
expected version and dependency constraints. Then create and publish a GitHub
Release from the matching tag. The release event starts the protected
workflow, which builds fresh artifacts and uploads them to PyPI.

The first stable release uses version `0.1.0`. Future releases must increment
the version before building or publishing again. Verify the published artifact
in a second clean virtual environment with:

```bash
python -m pip install mif-foundation
python -c "import core; print(core.__version__)"
mif-core catalog
```
