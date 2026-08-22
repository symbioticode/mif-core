# Public API

The supported public surface is exported from `core`:

```python
from core import (
    Certifier,
    CriteriaPolicy,
    MetricAdapter,
    MetricMetadata,
    StrategyAdapter,
    StrategyMetadata,
    default_catalog,
)
```

`core.__version__` exposes the installed package version and falls back to the
development version when imported directly from a checkout.

## Boundaries

- `StrategyAdapter` describes strategy signal and backtest behavior.
- `MetricAdapter` describes a metric calculated from one certified handoff.
- `MetricCertifier` validates the declared metric output shape and finiteness;
  invalid series or signal indices are included in the failure details.
- `StrategyMetadata` and `MetricMetadata` make the subject explicit.
- `StrategyRegistry` and `MetricRegistry` provide explicit name-based lookup.
- `default_catalog()` returns the shipped offline tests.
- `CriteriaPolicy` makes adaptive thresholds explicit.
- `Certifier` executes only the test IDs selected by the caller.
- `TestResult` defines the versioned schema used for each normalized test result.

`CertificationReport.to_dict()`, `to_json()`, and `to_text()` are the stable
report export methods. Metric certification results include the same asset,
calendar, coverage, DQF status, and assembly hash validity domain. CORE does not
fetch data; production callers provide a `DALHandoff` from `mif-dal-en`.
