# mif-core architecture

The first implementation follows the documented v5 design while keeping the
scope small and deterministic.

1. `StrategyMetadata` describes the strategy explicitly.
2. `StrategyAdapter` is the boundary between a strategy and CORE.
3. `TestCatalog` stores atomic, independently selectable tests.
4. `Certifier` executes only the tests named by the caller.
5. `CertificationReport` records status and validity domain.

The input boundary is one certified `DALHandoff` from `mif-dal-en`. CORE does
not fetch market data, repair data, or silently replace a failed DQF decision.

