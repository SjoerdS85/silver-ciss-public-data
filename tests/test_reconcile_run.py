import json
import unittest
from datetime import date
from decimal import Decimal
from pathlib import Path

from src.reconcile_run import load_baseline, model_impact
from src.model_stress import monthly_means, thresholds


class ReconciliationRunTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(Path("config/ciss_contract_v1.json").read_text())
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
        self.assertLess(abs(p75 - Decimal("0.17451666666666668")), Decimal("1e-16"))
        self.assertLess(abs(p95 - Decimal("0.43103642857142827")), Decimal("1e-16"))

    def test_model_impact_detects_no_change_when_official_equals_baseline(self):
        impact = model_impact(
            self.baseline,
            dict(self.baseline),
            date(2026, 9, 10),
        )
        self.assertEqual(impact["classification_change_count"], 0)


if __name__ == "__main__":
    unittest.main()
