import json
import tempfile
import unittest
from datetime import date
from decimal import Decimal
from pathlib import Path

from src.reconcile_run import assess_revision_governance, load_baseline, model_impact
from src.model_stress import monthly_means, thresholds


class ReconciliationRunTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(Path("config/ciss_contract_v1.json").read_text())
        cls.policy = json.loads(Path("config/revision_policy_v1.json").read_text())
        cls.baseline = load_baseline(
            "baseline/ciss_db31_accepted_20260910.csv",
            "baseline/MANIFEST.json",
            cls.contract,
        )

    def test_baseline_file_is_pinned(self):
        self.assertEqual(len(self.baseline), 12189)
        self.assertEqual(min(self.baseline), date(1980, 1, 3))
        self.assertEqual(max(self.baseline), date(2026, 9, 10))

    def test_accepted_september_thresholds_reproduce(self):
        completed = [
            (d, v)
            for d, v in self.baseline.items()
            if d <= date(2026, 8, 31)
        ]
        means = monthly_means(completed)
        p75, p95 = thresholds(means, "2026-09")
        tolerance = Decimal("5e-16")
        self.assertLess(abs(p75 - Decimal("0.17451666666666668")), tolerance)
        self.assertLess(abs(p95 - Decimal("0.43103642857142827")), tolerance)

    def test_model_impact_detects_no_change_when_official_equals_baseline(self):
        impact = model_impact(
            self.baseline,
            dict(self.baseline),
            date(2026, 9, 10),
        )
        self.assertEqual(impact["classification_change_count"], 0)

    def test_revision_policy_is_accepted_and_pins_fingerprint(self):
        self.assertEqual(self.policy["status"], "ACCEPTED")
        self.assertEqual(
            self.policy["accepted_revision_fingerprint"]["revision_report_sha256"],
            "08b533af543b5d586bf6830f20d26f9d8620665994e946cfe3add2b8bda91935",
        )

    def test_unexpected_revision_fingerprint_blocks(self):
        reconciliation = {
            "baseline_reconciliation_status": "HOLD_REVISION",
            "revision_count": 1,
            "missing_baseline_dates": [],
            "extra_pre_cut_dates": [],
            "value_diffs": [
                {
                    "date": "2026-09-10",
                    "baseline_value": "0.0359",
                    "official_raw_value": "0.0360",
                    "official_comparable_value": "0.0360",
                }
            ],
        }
        impact = {
            "classification_change_count": 0,
            "classification_months_compared": 559,
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "revision_report.csv"
            path.write_text("unexpected\n", encoding="utf-8")
            result = assess_revision_governance(
                path,
                "config/revision_policy_v1.json",
                reconciliation,
                impact,
            )
        self.assertEqual(result["status"], "HOLD_REVISION")
        self.assertFalse(result["fingerprint_match"])
        self.assertEqual(result["publication_gate"], "BLOCKED")


if __name__ == "__main__":
    unittest.main()
