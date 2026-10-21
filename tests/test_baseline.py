import unittest
from datetime import date
from decimal import Decimal

from src.reconcile import reconcile


class BaselineTests(unittest.TestCase):
    def test_exact_match_passes(self):
        baseline = {date(2026, 9, 9): Decimal("0.1000"), date(2026, 9, 10): Decimal("0.1100")}
        official = dict(baseline)
        official[date(2026, 9, 11)] = Decimal("0.1200")
        result = reconcile(baseline, official, cut=date(2026, 9, 10), expected_rows=2)
        self.assertEqual(result["baseline_reconciliation_status"], "PASS")
        self.assertEqual(result["first_new_date"], "2026-09-11")

    def test_revision_holds(self):
        baseline = {date(2026, 9, 10): Decimal("0.1000")}
        official = {date(2026, 9, 10): Decimal("0.1001")}
        result = reconcile(baseline, official, cut=date(2026, 9, 10), expected_rows=1)
        self.assertEqual(result["baseline_reconciliation_status"], "HOLD_REVISION")
        self.assertEqual(len(result["value_diffs"]), 1)


if __name__ == "__main__":
    unittest.main()
