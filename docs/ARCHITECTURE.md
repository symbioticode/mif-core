# mif-core architecture

The first implementation follows the documented v5 design while keeping the
scope small and deterministic.

1. `StrategyMetadata` describes the strategy explicitly.
2. `StrategyAdapter` is the boundary between a strategy and CORE.
3. `MetricAdapter` is the separate boundary for indicator and metric logic.
4. `MetricCertifier` validates the metric output contract and validity domain;
   metric checks are independent of strategy backtests.
5. `StrategyRegistry` names caller-registered strategies without discovery.
6. `MetricRegistry` names caller-registered metrics without discovery.
7. `TestCatalog` stores atomic, independently selectable tests.
8. `Certifier` executes only the tests named by the caller.
9. `CertificationReport` records status and validity domain.

The input boundary is one certified `DALHandoff` from `mif-dal-en`. CORE does
not fetch market data, repair data, or silently replace a failed DQF decision.

## Shipped offline catalogue

The initial catalogue contains six explicit tests:

- `T_HANDOFF_001` — verifies the DAL boundary;
- `T_SIGNAL_SHAPE_001` — verifies one signal per observation;
- `T_RETURN_INTEGRITY_001` — rejects empty, non-numeric, NaN, and infinite
  backtest returns;
- `T_WALK_FORWARD_001` — evaluates positive-return rates across explicit
  rolling train/test windows; the window size, initial training observations,
  step, and threshold are controlled by `CriteriaPolicy`;
- `T_STABILITY_001` — computes positive-return rate and selects a threshold
  from `StrategyMetadata.frequency` (`0.60` for low frequency, `0.50` otherwise).
- `T_LOOKAHEAD_001` — compares full-run and prefix signals to detect future-data
  influence.

The report also exposes a summary tier. `S` means every selected test passed;
`A` means at least 80% passed; `B` means at least 50% passed; `C` is the
conservative default for weaker evidence or no tests. The tier never hides the
individual results and is not a profitability claim.

Adaptive thresholds are supplied through `CriteriaPolicy`, which validates and
records the criteria used by stability and walk-forward tests. Callers can
inject a policy for an experiment without modifying test code.

These are deliberately small contracts, not a claim that a strategy is
profitable. Future tests can extend the same atomic interface without changing
the existing contracts.
