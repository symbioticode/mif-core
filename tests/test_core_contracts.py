import json
import tomllib
import unittest
from contextlib import redirect_stdout
from dataclasses import dataclass
from fractions import Fraction
from io import StringIO
from pathlib import Path

from core import (
    Certifier,
    CriteriaPolicy,
    MetricAdapter,
    MetricCertifier,
    MetricMetadata,
    MetricRegistry,
    StrategyAdapter,
    StrategyMetadata,
    StrategyRegistry,
    __version__,
    default_catalog,
)
from core import (
    TestCatalog as Catalog,
)
from core import (
    TestDefinition as Definition,
)
from core import (
    TestResult as Result,
)
from core.certification.report import CertificationReport
from core.certification.tiers import calculate_tier
from core.cli import main as cli_main
from core.integrations.dal import HandoffContractError


class Handoff:
    def __init__(self):
        self.stream = [1, 2, 3]

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


@dataclass(frozen=True)
class FrozenHandoff:
    stream: list
    asset_id: str = "BTC-USD"
    calendar: str = "CRYPTO_247"
    assembly_hash: str = "a" * 64
    handoff_timestamp: object = object()
    dal_version: str = "0.1.0"
    source_manifest: tuple = ({"source": "memory"},)
    coverage: str = "FULL"
    dqf_status: str = "PASS"
    dqf_mpi: float = 100.0
    dqf_version: str = "1.3.0"
    dqf_report: object = object()
    aqi: float = 100.0


class ExampleStrategy(StrategyAdapter):
    metadata = StrategyMetadata("example", "medium", "1D", 20, 5, ("crypto",))

    def calculate_signals(self, handoff):
        return [0] * len(handoff.stream)

    def backtest(self, handoff):
        return {"returns": [0.1, -0.02, 0.03, 0.01]}


class CoreContractTests(unittest.TestCase):
    def test_development_extra_includes_build_frontend(self):
        configuration = tomllib.loads(Path("pyproject.toml").read_text())
        development_dependencies = configuration["project"]["optional-dependencies"][
            "dev"
        ]
        self.assertTrue(
            any(
                dependency.split(">=", 1)[0] == "build"
                for dependency in development_dependencies
            )
        )

    def test_metadata_rejects_unknown_frequency(self):
        with self.assertRaises(ValueError):
            StrategyMetadata("bad", "unknown", "1D", 1, 1)
        with self.assertRaises(TypeError):
            StrategyMetadata(1, "medium", "1D", 1, 1)  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            StrategyMetadata("bad", "medium", "1D", True, 1)
        with self.assertRaises(TypeError):
            StrategyMetadata("bad", "medium", "1D", 1, 1, ["crypto"])  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            MetricMetadata("", "performance", "scalar")
        with self.assertRaises(TypeError):
            MetricMetadata("name", "performance", "scalar", 1)  # type: ignore[arg-type]

    def test_package_version_is_exposed(self):
        self.assertRegex(__version__, r"^\d+\.\d+\.\d+")

    def test_test_result_schema_is_versioned(self):
        result = Result("T", "test", "strategy", True, 1, {})
        self.assertEqual(result.to_dict()["schema_version"], 1)
        with self.assertRaises(TypeError):
            Result("T", "test", "strategy", 1, 1, {})  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            Result(
                "T",
                "test",
                "strategy",
                True,
                1,
                [],  # type: ignore[arg-type]
            )
        with self.assertRaises(TypeError):
            Result("T", "test", "strategy", True, 1, {}, schema_version=True)
        with self.assertRaises(ValueError):
            Result("T", "test", "strategy", True, 1, {}, schema_version=2)

    def test_metric_contract_requires_declared_output_kind(self):
        class ExampleMetric(MetricAdapter):
            metadata = MetricMetadata("return", "performance", "series")

            def calculate(self, handoff):
                return [0.1] * len(handoff.stream)

        self.assertEqual(ExampleMetric.metadata.output_kind, "series")
        with self.assertRaises(ValueError):
            MetricMetadata("bad", "performance", "unknown")

        result = MetricCertifier().certify(ExampleMetric(), Handoff())
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["schema_version"], 1)
        self.assertEqual(result["validity_domain"]["asset_scope"], "BTC-USD")
        self.assertEqual(result["validity_domain"]["coverage"], "FULL")
        self.assertEqual(result["validity_domain"]["assembly_hash"], "a" * 64)
        with self.assertRaises(TypeError):
            MetricCertifier().certify(object(), Handoff())  # type: ignore[arg-type]

    def test_metric_registry_rejects_duplicates(self):
        class ExampleMetric(MetricAdapter):
            metadata = MetricMetadata("return", "performance", "series")

            def calculate(self, handoff):
                return [0.1] * len(handoff.stream)

        registry = MetricRegistry()
        registry.register(ExampleMetric())
        self.assertEqual(registry.names(), ("return",))
        with self.assertRaises(ValueError):
            registry.register(ExampleMetric())
        with self.assertRaises(TypeError):
            registry.register(object())  # type: ignore[arg-type]
        with self.assertRaisesRegex(KeyError, "unknown metric name"):
            registry.get("missing")

    def test_metric_certifier_rejects_wrong_series_length_and_nan_scalar(self):
        class BadSeries(MetricAdapter):
            metadata = MetricMetadata("bad-series", "performance", "series")

            def calculate(self, handoff):
                return [1.0]

        class BadScalar(MetricAdapter):
            metadata = MetricMetadata("bad-scalar", "performance", "scalar")

            def calculate(self, handoff):
                return float("nan")

        self.assertEqual(
            MetricCertifier().certify(BadSeries(), Handoff())["status"], "FAIL"
        )
        self.assertEqual(
            MetricCertifier().certify(BadScalar(), Handoff())["status"], "FAIL"
        )

    def test_metric_certifier_rejects_nonfinite_or_nonnumeric_series_values(self):
        class BadSeries(MetricAdapter):
            metadata = MetricMetadata("bad-values", "performance", "series")

            def calculate(self, handoff):
                return [1.0, float("nan"), "bad"]

        result = MetricCertifier().certify(BadSeries(), Handoff())
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(result["details"]["invalid"][0]["reason"], "not finite")
        self.assertEqual(result["details"]["invalid"][1]["reason"], "not numeric")

    def test_metric_certifier_accepts_other_real_numeric_types(self):
        class FractionMetric(MetricAdapter):
            metadata = MetricMetadata("fraction", "performance", "scalar")

            def calculate(self, handoff):
                return Fraction(1, 2)

        result = MetricCertifier().certify(FractionMetric(), Handoff())
        self.assertEqual(result["status"], "PASS")

    def test_metric_exception_preserves_validity_domain(self):
        class RaisingMetric(MetricAdapter):
            metadata = MetricMetadata("raising", "performance", "scalar")

            def calculate(self, handoff):
                raise RuntimeError("metric failed")

        result = MetricCertifier().certify(RaisingMetric(), Handoff())
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(result["schema_version"], 1)
        self.assertEqual(result["validity_domain"]["asset_scope"], "BTC-USD")

    def test_strategy_registry_rejects_duplicates_and_sorts_names(self):
        registry = StrategyRegistry()
        registry.register(ExampleStrategy())
        self.assertEqual(registry.names(), ("example",))
        with self.assertRaises(ValueError):
            registry.register(ExampleStrategy())
        with self.assertRaises(TypeError):
            registry.register(object())  # type: ignore[arg-type]
        with self.assertRaisesRegex(KeyError, "unknown strategy name"):
            registry.get("missing")

    def test_test_definition_validates_identity_and_executor(self):
        with self.assertRaises(ValueError):
            Definition("", "name", "category", lambda **_: {})
        with self.assertRaises(TypeError):
            Definition("id", "name", "category", object())  # type: ignore[arg-type]
        with self.assertRaisesRegex(KeyError, "unknown test ID"):
            Catalog().get("missing")
        with self.assertRaises(TypeError):
            Catalog().register(object())  # type: ignore[arg-type]

    def test_certifier_runs_only_selected_tests(self):
        catalog = Catalog()
        catalog.register(
            Definition("T_PASS", "pass", "integrity", lambda **_: {"passed": True})
        )
        report = Certifier(catalog).certify(ExampleStrategy(), Handoff(), ["T_PASS"])
        self.assertEqual(report.status, "PASS")
        self.assertEqual(report.validity_domain["asset_scope"], "BTC-USD")
        self.assertEqual(report.validity_domain["assembly_hash"], "a" * 64)
        self.assertEqual(report.tests_run["T_PASS"]["status"], "PASS")
        self.assertEqual(report.to_dict()["strategy_name"], "example")
        self.assertEqual(report.tier, "S")
        self.assertEqual(json.loads(report.to_json())["tier"], "S")
        self.assertIn("Strategy: example", report.to_text())
        self.assertIn("T_PASS [PASS]", report.to_text())
        self.assertIn("value=None", report.to_text())

    def test_certifier_rejects_empty_protocol(self):
        catalog = Catalog()
        with self.assertRaises(ValueError):
            Certifier(catalog).certify(ExampleStrategy(), Handoff(), [])
        with self.assertRaises(TypeError):
            Certifier(catalog).certify(ExampleStrategy(), Handoff(), "T_PASS")  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            Certifier(catalog).certify(ExampleStrategy(), Handoff(), [""])
        with self.assertRaises(TypeError):
            Certifier(catalog).certify(object(), Handoff(), ["T_PASS"])  # type: ignore[arg-type]

    def test_certifier_rejects_duplicate_test_ids(self):
        catalog = Catalog()
        catalog.register(
            Definition("T_PASS", "pass", "integrity", lambda **_: {"passed": True})
        )
        with self.assertRaises(ValueError):
            Certifier(catalog).certify(
                ExampleStrategy(), Handoff(), ["T_PASS", "T_PASS"]
            )

    def test_certifier_rejects_invalid_dqf_status(self):
        catalog = Catalog()
        catalog.register(
            Definition("T_PASS", "pass", "integrity", lambda **_: {"passed": True})
        )
        handoff = Handoff()
        handoff.dqf_status = "FAIL"
        with self.assertRaises(HandoffContractError):
            Certifier(catalog).certify(ExampleStrategy(), handoff, ["T_PASS"])

    def test_dal_boundary_rejects_ambiguous_quality_scores(self):
        handoff = Handoff()
        handoff.aqi = float("nan")
        with self.assertRaises(HandoffContractError):
            Certifier(default_catalog()).certify(
                ExampleStrategy(), handoff, ["T_HANDOFF_001"]
            )
        handoff.aqi = True
        with self.assertRaises(HandoffContractError):
            Certifier(default_catalog()).certify(
                ExampleStrategy(), handoff, ["T_HANDOFF_001"]
            )

    def test_dal_boundary_rejects_empty_stream(self):
        handoff = Handoff()
        handoff.stream = []
        with self.assertRaisesRegex(HandoffContractError, "stream must not be empty"):
            Certifier(default_catalog()).certify(
                ExampleStrategy(), handoff, ["T_HANDOFF_001"]
            )

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
        catalog = Catalog()
        catalog.register(
            Definition(
                "T_RAISE",
                "raising test",
                "strategy",
                lambda **_: 1 / 0,  # type: ignore[arg-type]
            )
        )
        report = Certifier(catalog).certify(ExampleStrategy(), Handoff(), ["T_RAISE"])
        self.assertEqual(report.status, "FAIL")
        self.assertEqual(
            report.tests_run["T_RAISE"]["details"]["error"], "division by zero"
        )

    def test_non_mapping_test_result_becomes_explicit_failure(self):
        catalog = Catalog()
        catalog.register(
            Definition(
                "T_BAD_RESULT",
                "bad result",
                "strategy",
                lambda **_: 42,  # type: ignore[arg-type]
            )
        )
        report = Certifier(catalog).certify(
            ExampleStrategy(), Handoff(), ["T_BAD_RESULT"]
        )
        result = report.tests_run["T_BAD_RESULT"]
        self.assertEqual(report.status, "FAIL")
        self.assertEqual(result["details"]["error"], "test returned int, expected dict")

    def test_tiers_are_deterministic_and_empty_is_conservative(self):
        self.assertEqual(calculate_tier({}), "C")
        self.assertEqual(
            calculate_tier({"a": {"passed": True}, "b": {"passed": False}}), "B"
        )
        self.assertEqual(
            calculate_tier({"a": {"passed": True}, "b": {"passed": True}}), "S"
        )

    def test_certification_report_rejects_invalid_status_and_tier(self):
        with self.assertRaises(ValueError):
            CertificationReport("example", {}, "UNKNOWN", {})
        with self.assertRaises(ValueError):
            CertificationReport("example", {}, "PASS", {}, tier="D")
        with self.assertRaises(TypeError):
            CertificationReport("example", [], "PASS", {})  # type: ignore[arg-type]

    def test_certification_report_serializes_arbitrary_details_as_repr(self):
        class OpaqueDetail:
            def __repr__(self):
                return "<opaque-detail>"

        report = CertificationReport(
            "example",
            {
                "T_OPAQUE": {
                    "test_id": "T_OPAQUE",
                    "status": "FAIL",
                    "test_name": "opaque",
                    "value": None,
                    "details": {"payload": OpaqueDetail()},
                }
            },
            "FAIL",
            {},
        )
        self.assertEqual(
            json.loads(report.to_json())["tests_run"]["T_OPAQUE"]["details"]["payload"],
            "<opaque-detail>",
        )
        self.assertIn('"payload": "<opaque-detail>"', report.to_text())

    def test_criteria_policy_is_validated_and_injectable(self):
        with self.assertRaises(ValueError):
            CriteriaPolicy(default_positive_rate=1.1)
        with self.assertRaises(TypeError):
            CriteriaPolicy(default_positive_rate=True)
        with self.assertRaises(TypeError):
            CriteriaPolicy(walk_forward_step=True)
        with self.assertRaises(ValueError):
            CriteriaPolicy(walk_forward_train_observations=0)
        policy = CriteriaPolicy(default_positive_rate=0.80)
        report = Certifier(default_catalog(policy)).certify(
            ExampleStrategy(), Handoff(), ["T_STABILITY_001"]
        )
        self.assertEqual(report.status, "FAIL")
        self.assertEqual(report.tests_run["T_STABILITY_001"]["threshold"], 0.80)

    def test_cli_catalog_is_available(self):
        self.assertEqual(cli_main(["catalog"]), 0)

    def test_cli_version_is_available(self):
        with self.assertRaises(SystemExit) as raised:
            cli_main(["--version"])
        self.assertEqual(raised.exception.code, 0)

    def test_cli_demo_is_reproducible(self):
        self.assertEqual(cli_main(["demo"]), 0)

    def test_cli_metric_demo_is_available(self):
        self.assertEqual(cli_main(["metric-demo"]), 0)

    def test_cli_demo_supports_human_readable_output(self):
        output = StringIO()
        with redirect_stdout(output):
            self.assertEqual(cli_main(["demo", "--format", "text"]), 0)
        self.assertIn("Strategy: demo", output.getvalue())
        self.assertIn("T_HANDOFF_001 [PASS]", output.getvalue())

    def test_cli_demo_can_select_tests(self):
        output = StringIO()
        with redirect_stdout(output):
            self.assertEqual(
                cli_main(["demo", "--format", "text", "--tests", "T_SIGNAL_SHAPE_001"]),
                0,
            )
        self.assertIn("T_SIGNAL_SHAPE_001 [PASS]", output.getvalue())
        self.assertNotIn("T_HANDOFF_001", output.getvalue())

    def test_cli_metric_demo_supports_human_readable_output(self):
        output = StringIO()
        with redirect_stdout(output):
            self.assertEqual(cli_main(["metric-demo", "--format", "text"]), 0)
        self.assertIn("Metric: demo-mean v0.1.0", output.getvalue())
        self.assertIn("Status: PASS", output.getvalue())

    def test_stability_uses_frequency_aware_threshold(self):
        report = Certifier(default_catalog()).certify(
            ExampleStrategy(), Handoff(), ["T_STABILITY_001"]
        )
        self.assertEqual(report.status, "PASS")
        self.assertEqual(report.tests_run["T_STABILITY_001"]["threshold"], 0.50)

    def test_stability_reports_zero_and_negative_observations(self):
        class MixedSignStrategy(ExampleStrategy):
            def backtest(self, handoff):
                return {"returns": [0.1, 0.0, -0.1, 0.0]}

        report = Certifier(default_catalog()).certify(
            MixedSignStrategy(), Handoff(), ["T_STABILITY_001"]
        )
        result = report.tests_run["T_STABILITY_001"]
        self.assertEqual(report.status, "FAIL")
        self.assertEqual(result["value"], 0.25)
        self.assertEqual(result["details"]["positive_observations"], 1)
        self.assertEqual(result["details"]["zero_observations"], 2)
        self.assertEqual(result["details"]["negative_observations"], 1)

    def test_return_integrity_accepts_finite_numeric_returns(self):
        report = Certifier(default_catalog()).certify(
            ExampleStrategy(), Handoff(), ["T_RETURN_INTEGRITY_001"]
        )
        self.assertEqual(report.status, "PASS")

    def test_return_integrity_rejects_nan_and_infinity(self):
        class CorruptStrategy(ExampleStrategy):
            def backtest(self, handoff):
                return {"returns": [0.1, float("nan"), float("inf")]}

        report = Certifier(default_catalog()).certify(
            CorruptStrategy(), Handoff(), ["T_RETURN_INTEGRITY_001"]
        )
        self.assertEqual(report.status, "FAIL")
        self.assertEqual(
            len(report.tests_run["T_RETURN_INTEGRITY_001"]["details"]["invalid"]), 2
        )

    def test_stability_reports_invalid_returns_when_selected_alone(self):
        class CorruptStrategy(ExampleStrategy):
            def backtest(self, handoff):
                return {"returns": [0.1, float("nan"), "bad"]}

        report = Certifier(default_catalog()).certify(
            CorruptStrategy(), Handoff(), ["T_STABILITY_001"]
        )
        result = report.tests_run["T_STABILITY_001"]
        self.assertEqual(report.status, "FAIL")
        self.assertEqual(result["details"]["reason"], "invalid returns")
        self.assertEqual(result["details"]["invalid"][1]["reason"], "not numeric")

    def test_walk_forward_accepts_positive_out_of_sample_rate(self):
        report = Certifier(default_catalog()).certify(
            ExampleStrategy(), Handoff(), ["T_WALK_FORWARD_001"]
        )
        self.assertEqual(report.status, "PASS")

    def test_walk_forward_rejects_negative_out_of_sample_rate(self):
        class DegradingStrategy(ExampleStrategy):
            def backtest(self, handoff):
                return {"returns": [0.1, 0.1, -0.1, -0.1]}

        report = Certifier(default_catalog()).certify(
            DegradingStrategy(), Handoff(), ["T_WALK_FORWARD_001"]
        )
        self.assertEqual(report.status, "FAIL")

    def test_walk_forward_reports_rolling_windows(self):
        class MixedStrategy(ExampleStrategy):
            def backtest(self, handoff):
                return {"returns": [0.1, 0.1, 0.1, 0.1, -0.1, -0.1]}

        policy = CriteriaPolicy(
            walk_forward_test_fraction=0.33,
            walk_forward_train_observations=2,
            walk_forward_step=1,
        )
        report = Certifier(default_catalog(policy)).certify(
            MixedStrategy(), Handoff(), ["T_WALK_FORWARD_001"]
        )
        result = report.tests_run["T_WALK_FORWARD_001"]
        self.assertEqual(report.status, "FAIL")
        self.assertGreater(result["details"]["window_count"], 1)
        self.assertEqual(
            len(result["details"]["windows"]), result["details"]["window_count"]
        )

    def test_walk_forward_reports_invalid_returns_explicitly(self):
        class CorruptStrategy(ExampleStrategy):
            def backtest(self, handoff):
                return {"returns": [0.1, float("nan"), "bad", 0.2]}

        report = Certifier(default_catalog()).certify(
            CorruptStrategy(), Handoff(), ["T_WALK_FORWARD_001"]
        )
        result = report.tests_run["T_WALK_FORWARD_001"]
        self.assertEqual(report.status, "FAIL")
        self.assertEqual(result["details"]["reason"], "invalid returns")
        self.assertEqual(result["details"]["invalid"][0]["index"], 1)

    def test_walk_forward_rejects_insufficient_test_sample(self):
        class ShortStrategy(ExampleStrategy):
            def backtest(self, handoff):
                return {"returns": [0.1]}

        report = Certifier(default_catalog()).certify(
            ShortStrategy(), Handoff(), ["T_WALK_FORWARD_001"]
        )
        self.assertEqual(report.status, "FAIL")
        self.assertIn(
            "insufficient", report.tests_run["T_WALK_FORWARD_001"]["details"]["reason"]
        )

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

    def test_lookahead_supports_frozen_dal_handoff(self):
        report = Certifier(default_catalog()).certify(
            ExampleStrategy(), FrozenHandoff([1, 2, 3]), ["T_LOOKAHEAD_001"]
        )
        self.assertEqual(report.status, "PASS")

    def test_lookahead_rejects_insufficient_sample(self):
        report = Certifier(default_catalog()).certify(
            ExampleStrategy(), FrozenHandoff([1]), ["T_LOOKAHEAD_001"]
        )
        result = report.tests_run["T_LOOKAHEAD_001"]
        self.assertEqual(report.status, "FAIL")
        self.assertEqual(result["details"]["reason"], "insufficient sample")
        self.assertEqual(result["details"]["observations"], 1)

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
