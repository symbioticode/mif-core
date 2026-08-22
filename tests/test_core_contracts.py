import unittest

from core import Certifier, StrategyAdapter, StrategyMetadata, TestCatalog, TestDefinition, default_catalog
from core.certification.tiers import calculate_tier
from core.integrations.dal import HandoffContractError


class Handoff:
    stream = [1, 2, 3]
    asset_id = "BTC-USD"
    calendar = "CRYPTO_247"
    assembly_hash = "a" * 64
    handoff_timestamp = object()
    dal_version = "0.1.0"
    source_manifest = ({"source": "memory"},)
    coverage = "FULL"
    dqf_status = "PASS"
    dqf_mpi = 100.0
    dqf_version = "1.3.0"
    dqf_report = object()
    aqi = 100.0


class ExampleStrategy(StrategyAdapter):
    metadata = StrategyMetadata("example", "medium", "1D", 20, 5, ("crypto",))

    def calculate_signals(self, handoff):
        return [0] * len(handoff.stream)

    def backtest(self, handoff):
        return {"returns": [0.1, -0.02, 0.03, 0.01]}


class CoreContractTests(unittest.TestCase):
    def test_metadata_rejects_unknown_frequency(self):
        with self.assertRaises(ValueError):
            StrategyMetadata("bad", "unknown", "1D", 1, 1)

    def test_certifier_runs_only_selected_tests(self):
        catalog = TestCatalog()
        catalog.register(TestDefinition("T_PASS", "pass", "integrity", lambda **_: {"passed": True}))
        report = Certifier(catalog).certify(ExampleStrategy(), Handoff(), ["T_PASS"])
        self.assertEqual(report.status, "PASS")
        self.assertEqual(report.validity_domain["asset_scope"], "BTC-USD")
        self.assertEqual(report.validity_domain["assembly_hash"], "a" * 64)
        self.assertEqual(report.tests_run["T_PASS"]["status"], "PASS")
        self.assertEqual(report.to_dict()["strategy_name"], "example")
        self.assertEqual(report.tier, "S")

    def test_certifier_rejects_empty_protocol(self):
        catalog = TestCatalog()
        with self.assertRaises(ValueError):
            Certifier(catalog).certify(ExampleStrategy(), Handoff(), [])

    def test_certifier_rejects_invalid_dqf_status(self):
        catalog = TestCatalog()
        catalog.register(TestDefinition("T_PASS", "pass", "integrity", lambda **_: {"passed": True}))
        handoff = Handoff()
        handoff.dqf_status = "FAIL"
        with self.assertRaises(HandoffContractError):
            Certifier(catalog).certify(ExampleStrategy(), handoff, ["T_PASS"])

    def test_builtin_catalog_certifies_signal_shape(self):
        report = Certifier(default_catalog()).certify(
            ExampleStrategy(), Handoff(), ["T_HANDOFF_001", "T_SIGNAL_SHAPE_001"]
        )
        self.assertEqual(report.status, "PASS")

    def test_builtin_catalog_detects_signal_length_mutation(self):
        class MutatedStrategy(ExampleStrategy):
            def calculate_signals(self, handoff):
                return [0]

        report = Certifier(default_catalog()).certify(
            MutatedStrategy(), Handoff(), ["T_SIGNAL_SHAPE_001"]
        )
        self.assertEqual(report.status, "FAIL")

    def test_test_exception_becomes_explicit_failure(self):
        catalog = TestCatalog()
        catalog.register(TestDefinition("T_RAISE", "raising test", "strategy", lambda **_: 1 / 0))
        report = Certifier(catalog).certify(ExampleStrategy(), Handoff(), ["T_RAISE"])
        self.assertEqual(report.status, "FAIL")
        self.assertEqual(report.tests_run["T_RAISE"]["details"]["error"], "division by zero")

    def test_tiers_are_deterministic_and_empty_is_conservative(self):
        self.assertEqual(calculate_tier({}), "C")
        self.assertEqual(calculate_tier({"a": {"passed": True}, "b": {"passed": False}}), "B")
        self.assertEqual(calculate_tier({"a": {"passed": True}, "b": {"passed": True}}), "S")

    def test_stability_uses_frequency_aware_threshold(self):
        report = Certifier(default_catalog()).certify(
            ExampleStrategy(), Handoff(), ["T_STABILITY_001"]
        )
        self.assertEqual(report.status, "PASS")
        self.assertEqual(report.tests_run["T_STABILITY_001"]["threshold"], 0.50)

    def test_stability_rejects_low_frequency_below_threshold(self):
        class LowFrequencyStrategy(ExampleStrategy):
            metadata = StrategyMetadata("low", "low", "1W", 2, 90)

            def backtest(self, handoff):
                return {"returns": [0.1, -0.1]}

        report = Certifier(default_catalog()).certify(
            LowFrequencyStrategy(), Handoff(), ["T_STABILITY_001"]
        )
        self.assertEqual(report.status, "FAIL")
        self.assertEqual(report.tests_run["T_STABILITY_001"]["threshold"], 0.60)

    def test_lookahead_test_accepts_causal_strategy(self):
        report = Certifier(default_catalog()).certify(
            ExampleStrategy(), Handoff(), ["T_LOOKAHEAD_001"]
        )
        self.assertEqual(report.status, "PASS")

    def test_lookahead_test_rejects_future_dependent_strategy(self):
        class LeakingStrategy(ExampleStrategy):
            def calculate_signals(self, handoff):
                future = handoff.stream[-1]
                return [future] * len(handoff.stream)

        report = Certifier(default_catalog()).certify(
            LeakingStrategy(), Handoff(), ["T_LOOKAHEAD_001"]
        )
        self.assertEqual(report.status, "FAIL")


if __name__ == "__main__":
    unittest.main()
