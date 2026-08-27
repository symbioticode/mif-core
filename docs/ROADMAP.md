# Roadmap

`mif-core` currently provides a deterministic contract and test foundation. It
does not claim that a strategy is profitable or production-ready merely
because its selected tests pass.

## Current baseline

- frozen metadata contracts for metrics and strategies;
- explicit registries with no implicit discovery;
- canonical `DALHandoff` boundary validation;
- offline atomic tests for shape, return integrity, stability, walk-forward,
  and prefix causality;
- JSON reports, summary tiers, and CLI demonstrations;
- reproducible source and wheel builds with CI.

## Next implementation phases

1. Done: metric-specific contract tests now exercise series shape, scalar
   finiteness, invalid values, exceptions, and validity-domain preservation
   without using a strategy backtest.
2. Done: configurable rolling windows now expose train observations, test
   fraction, step, per-window outcomes, and aggregate reporting.
3. Done: human-readable reports preserve values, thresholds, and details while
   JSON remains the machine contract.
4. Done: CI imports the canonical `DALHandoff`, runs the integration suite, and
  covers Python 3.11 and 3.12. Python 3.13 is deferred until the canonical
  `mif-dal` dependency can install its NumPy constraint on that interpreter.
5. Done: the stable `0.1` API was tagged and published as `mif-foundation`
   0.1.0.

Every phase must preserve explicit selection, provenance, deterministic
offline tests, and transparent failure details.
