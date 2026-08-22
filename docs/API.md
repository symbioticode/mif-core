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

## Boundaries

- `StrategyAdapter` describes strategy signal and backtest behavior.
- `MetricAdapter` describes a metric calculated from one certified handoff.
- `StrategyMetadata` and `MetricMetadata` make the subject explicit.
- `default_catalog()` returns the shipped offline tests.
- `CriteriaPolicy` makes adaptive thresholds explicit.
- `Certifier` executes only the test IDs selected by the caller.

`CertificationReport.to_dict()` and `CertificationReport.to_json()` are the
stable report export methods. CORE does not fetch data; production callers
provide a `DALHandoff` from `mif-dal-en`.
