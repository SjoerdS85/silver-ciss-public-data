import unittest
from datetime import date
from decimal import Decimal

from src.reconcile import reconcile


class BaselineTests(unittest.TestCase):
    def test_representation_only_difference_passes(self):
        baseline = {date(1980, 1, 3): Decimal("0.1356")}
        official = {date(1980, 1, 3): Decimal("0.135571")}
        result = reconcile(baseline, official, cut=date(1980, 1, 3), expected_rows=1)
        self.assertEqual(result["baseline_reconciliation_status"], "PASS")
        self.assertEqual(result["matched_count"], 1)
        self.assertEqual(result["revision_count"], 0)

    def test_revision_holds_after_4dp_normalization(self):
        baseline = {date(1999, 4, 14): Decimal("0.0515")}
        official = {date(1999, 4, 14): Decimal("0.051593234783140776")}
        result = reconcile(baseline, official, cut=date(1999, 4, 14), expected_rows=1)
        self.assertEqual(result["baseline_reconciliation_status"], "HOLD_REVISION")
        self.assertEqual(result["revision_count"], 1)
        self.assertEqual(result["value_diffs"][0]["official_comparable_value"], "0.0516")

    def test_new_dates_are_reported(self):
        baseline = {date(2026, 9, 10): Decimal("0.0359")}
        official = {
            date(2026, 9, 10): Decimal("0.0359"),
            date(2026, 9, 11): Decimal("0.0312"),
        }
        result = reconcile(baseline, official, cut=date(2026, 9, 10), expected_rows=1)
        self.assertEqual(result["first_new_date"], "2026-09-11")


if __name__ == "__main__":
    unittest.main()
