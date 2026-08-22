# mif-core

The metric and strategy qualification layer of the Metric Integrity Framework.

`mif-core` sits above the two canonical infrastructure projects:

```text
mif-dqf  → certifies data quality
mif-dal  → assembles and hands off certified data
mif-core → qualifies metrics and strategies
```

This first increment defines explicit contracts and a deterministic offline
catalogue. Tests are selected explicitly; no hidden one-size-fits-all protocol
is applied.

## Included test catalogue

The package currently ships six offline checks: DAL handoff readiness, signal
shape, adaptive positive-return stability, return integrity, configurable
rolling out-of-sample consistency, and prefix causality (look-ahead detection). They
are deliberately small building blocks, not a complete profitability
guarantee.

## Development

```bash
python -m pip install -e '.[dev]'
python -m pytest
python -m build
```

The published distribution is named `metric-integrity-core` on PyPI. The
import package and command remain `core` and `mif-core` respectively; the
longer distribution name makes the PyPI project unambiguous.

```bash
mif-core catalog
mif-core --version
mif-core demo
mif-core metric-demo
mif-core demo --format text
mif-core metric-demo --format text
mif-core demo --tests T_HANDOFF_001,T_LOOKAHEAD_001
```

An external strategy can implement `StrategyAdapter` and be certified against
an explicit list of tests. See `examples/certify_strategy.py` for an offline
example; production callers should supply the real `DALHandoff` from
`mif-dal-en`.

`examples/certify_metric.py` shows the corresponding metric contract.

See [`docs/API.md`](docs/API.md) for the supported public surface.
See [`docs/ROADMAP.md`](docs/ROADMAP.md) for current limits and next phases.
See [`docs/PUBLISHING.md`](docs/PUBLISHING.md) for the PyPI release path.

## Status

Development implementation based on the documented MIF v5 architecture. The
architecture file contains a historical brainstorming version marker; the
provenance decision is recorded in `docs/PROVENANCE.md`.

## Test

```bash
python3 -m unittest discover -s tests -v
```
