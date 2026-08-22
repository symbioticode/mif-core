# Publishing `metric-integrity-core`

The repository is `symbioticode/mif-core`, while the PyPI distribution is
`metric-integrity-core`. The import package remains `core` and the optional
CLI remains `mif-core`.

## One-time PyPI setup

1. Create the PyPI project configuration for `metric-integrity-core`.
2. Add a Trusted Publisher using:
   - owner: `symbioticode`;
   - repository: `mif-core`;
   - workflow: `.github/workflows/publish.yml`;
   - environment: empty, unless a PyPI environment is deliberately chosen.
3. Do not add a PyPI API token to GitHub secrets. The workflow requests an
   OIDC identity token and uses Trusted Publishing.

## Release checklist

Before publishing a release:

```bash
python -m pip install -e '.[dev]'
python -m pytest
python -m ruff check core tests examples
python -m build
```

Check that both artifacts in `dist/` are named
`metric_integrity_core-<version>.*`, then create and publish a GitHub Release.
The release event starts the protected workflow, which builds fresh artifacts
and uploads them to PyPI.

The first release should use a new version (for example `0.1.0`) and should
be tested in a clean virtual environment with:

```bash
python -m pip install metric-integrity-core
python -c "import core; print(core.__version__)"
mif-core catalog
```
