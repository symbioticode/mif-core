"""Integration checks against the canonical mif-dal handoff contract."""

import unittest
from datetime import datetime, timezone

try:
    import pandas as pd
    from dal.core.handoff import DALHandoff
except ImportError:  # optional locally; CI installs mif-dal and its dependencies
    pd = None
    DALHandoff = None

from core import validate_dal_handoff


@unittest.skipIf(pd is None or DALHandoff is None, "mif-dal dependencies unavailable")
class CanonicalDalIntegrationTests(unittest.TestCase):
    def make_handoff(self):
        index = pd.date_range("2026-01-01", periods=3, tz="UTC")
        stream = pd.DataFrame(
            {column: [1.0, 1.1, 1.2] for column in ("open", "high", "low", "close", "volume")},
            index=index,
        )
        return DALHandoff(
            stream=stream,
            asset_id="TEST-USD",
            calendar="CRYPTO_247",
            assembly_hash="a" * 64,
            handoff_timestamp=datetime.now(timezone.utc),
            dal_version="0.1.0",
            source_manifest=({"source": "in_memory"},),
            coverage="FULL",
            truncated_days=0,
            dqf_status="PASS",
            dqf_mpi=100.0,
            dqf_version="1.3.0",
            dqf_version_target="1.3.0",
            dqf_report=object(),
            aqi=100.0,
        )

    def test_canonical_handoff_passes_core_boundary(self):
        handoff = self.make_handoff()
        validate_dal_handoff(handoff)
        self.assertEqual(handoff.asset_id, "TEST-USD")


if __name__ == "__main__":
    unittest.main()
