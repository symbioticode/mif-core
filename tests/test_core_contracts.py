import unittest

from core import Certifier, StrategyAdapter, StrategyMetadata, TestCatalog, TestDefinition


class Handoff:
    asset_id = "BTC-USD"


class ExampleStrategy(StrategyAdapter):
    metadata = StrategyMetadata("example", "medium", "1D", 20, 5, ("crypto",))

    def calculate_signals(self, handoff):
        return []

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


if __name__ == "__main__":
    unittest.main()

