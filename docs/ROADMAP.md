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

1. Add a formal `TestResult` schema and version it independently from the
   package.
2. Add metric-specific atomic tests without coupling them to a strategy
   backtest contract.
3. Replace the minimal two-half walk-forward check with configurable rolling
   windows and an explicit minimum-sample policy.
4. Add a human-readable report renderer while preserving JSON as the machine
   contract.
5. Run the canonical DAL integration suite with real `DALHandoff` objects in
   CI and document the exact dependency matrix.
6. Define a stable `0.1` API and only then prepare the first PyPI release.

Every phase must preserve explicit selection, provenance, deterministic
offline tests, and transparent failure details.
