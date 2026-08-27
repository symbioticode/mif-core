# Changelog

## 0.2.0 — 2026-08-26

- Standardized public validation errors: invalid field types raise `TypeError`,
  while invalid values of the expected type raise `ValueError`.
- Added explicit positive, zero, and negative observation counts to stability
  diagnostics without changing the verdict calculation.
- Confirmed the public naming contract: repository, product, and CLI
  `mif-core`; PyPI distribution `mif-foundation`; Python import package `core`.

## 0.1.0

- Named the PyPI distribution `mif-foundation`; the import package remains
  `core` and the CLI remains `mif-core`.
- Added configurable rolling walk-forward windows with explicit train/test
  policy and per-window reporting.
- Added finite/numeric validation and explicit diagnostics for metric and
  strategy returns.
- Added human-readable CLI and certification report output alongside JSON.
- Added explicit CLI test selection and duplicate-selection rejection.
- Hardened adapter, metadata, registry, catalog, report, and DAL boundary
  validation with diagnostics for invalid inputs.
- Added NumPy-compatible real-number handling for metric outputs and DAL
  quality scores.
- Enforced Ruff formatting in CI.
- Added Python 3.13, canonical DAL import, mypy, and artifact metadata checks
  to CI.
- Updated the protected GitHub Release workflow and PyPI publishing guide.

- Declared the supported Python range as 3.11–3.12, matching the current
  `mif-dal` and NumPy compatibility boundary.
- Prepared the first stable PyPI release as `mif-foundation`.

- Added `StrategyMetadata` and `StrategyAdapter`.
- Added explicit `TestCatalog` and `Certifier` contracts.
- Added DAL handoff validation.
- Added offline handoff, signal-shape, stability, and look-ahead tests.
- Added normalized reports and transparent S/A/B/C summary tiers.
- Added explicit `MetricAdapter` and `MetricMetadata` contracts.
- Added metric and strategy registries, metric output certification, CLI demos,
  and JSON report serialization.
