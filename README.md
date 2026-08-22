# mif-core

The metric and strategy qualification layer of the Metric Integrity Framework.

`mif-core` sits above the two canonical infrastructure projects:

```text
mif-dqf  → certifies data quality
mif-dal  → assembles and hands off certified data
mif-core → qualifies metrics and strategies
```

This first increment defines contracts only. Tests are selected explicitly; no
hidden one-size-fits-all protocol is applied.

## Included test catalogue

The package currently ships four offline checks: DAL handoff readiness,
signal shape, adaptive positive-return stability, and prefix causality
(look-ahead detection). They are deliberately small building blocks, not a
complete profitability guarantee.

## Development

```bash
python -m pip install -e '.[dev]'
python -m pytest
python -m build
```

An external strategy can implement `StrategyAdapter` and be certified against
an explicit list of tests. See `examples/certify_strategy.py` for an offline
example; production callers should supply the real `DALHandoff` from
`mif-dal-en`.

`examples/certify_metric.py` shows the corresponding metric contract.

See [`docs/API.md`](docs/API.md) for the supported public surface.

## Status

Bootstrap implementation based on the documented MIF v5 architecture. The
architecture file is historically named v5 but declares version 9.0.0; this
provenance ambiguity is intentionally recorded in `docs/PROVENANCE.md`.

## Test

```bash
python3 -m unittest discover -s tests -v
```
