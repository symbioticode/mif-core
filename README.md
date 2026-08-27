# mif-core

[![Tests](https://github.com/symbioticode/mif-core/actions/workflows/ci.yml/badge.svg)](https://github.com/symbioticode/mif-core/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/mif-foundation)](https://pypi.org/project/mif-foundation/)
[![Python versions](https://img.shields.io/pypi/pyversions/mif-foundation)](https://pypi.org/project/mif-foundation/)
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow)](LICENSE)

The metric and strategy qualification layer of the Metric Integrity Framework.

`mif-core` sits above the two canonical infrastructure projects:

```text
mif-dqf  → certifies data quality
mif-dal  → assembles and hands off certified data
mif-core → qualifies metrics and strategies
```

| Layer | Repository | PyPI distribution | Python import | Responsibility |
|---|---|---|---|---|
| MIF-DQF | [`symbioticode/mif-dqf`](https://github.com/symbioticode/mif-dqf) | [`mif-dqf`](https://pypi.org/project/mif-dqf/) | `dqf` | Certify the physical and structural quality of market data. |
| MIF-DAL | [`symbioticode/mif-dal`](https://github.com/symbioticode/mif-dal) | [`mif-dal`](https://pypi.org/project/mif-dal/) | `dal` | Assemble reproducible streams and produce certified handoffs. |
| MIF Core | [`symbioticode/mif-core`](https://github.com/symbioticode/mif-core) | [`mif-foundation`](https://pypi.org/project/mif-foundation/) | `core` | Qualify metrics and strategies against explicit offline tests. |

The three packages form one directional contract: DQF certifies the data, DAL
assembles and transports the certified handoff, and Core evaluates what is
computed from that handoff. Each package remains installable and versioned
independently.

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

The published distribution is named `mif-foundation` on PyPI. The
import package and command remain `core` and `mif-core` respectively; the
longer distribution name makes the PyPI project unambiguous.

## Supported Python versions

The current release supports Python 3.11 and 3.12. Python 3.13 support is
deferred because the canonical `mif-dal` dependency currently requires a
NumPy version without a compatible Python 3.13 distribution.

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
`mif-dal`.

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
