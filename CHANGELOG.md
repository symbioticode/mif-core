# Changelog

## Unreleased

- Renamed the PyPI distribution to `metric-integrity-core`; the import package
  remains `core` and the CLI remains `mif-core`.
- Added configurable rolling walk-forward windows with explicit train/test
  policy and per-window reporting.
- Added finite/numeric validation and explicit diagnostics for metric and
  strategy returns.
- Added human-readable CLI and certification report output alongside JSON.
- Added Python 3.13, canonical DAL import, mypy, and artifact metadata checks
  to CI.
- Updated the protected GitHub Release workflow and PyPI publishing guide.

## 0.1.0.dev1

- Added `StrategyMetadata` and `StrategyAdapter`.
- Added explicit `TestCatalog` and `Certifier` contracts.
- Added DAL handoff validation.
- Added offline handoff, signal-shape, stability, and look-ahead tests.
- Added normalized reports and transparent S/A/B/C summary tiers.
- Added explicit `MetricAdapter` and `MetricMetadata` contracts.
- Added metric and strategy registries, metric output certification, CLI demos,
  and JSON report serialization.
