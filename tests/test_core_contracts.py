import unittest

from core import Certifier, StrategyAdapter, StrategyMetadata, TestCatalog, TestDefinition, default_catalog
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
        return {"return": 0.0}


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


if __name__ == "__main__":
    unittest.main()
