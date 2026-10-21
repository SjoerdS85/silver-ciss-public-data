import unittest
from decimal import Decimal

from src.model_stress import apply_partial, classify, completed_state
from src.validate import percentile_inc


class StressTests(unittest.TestCase):
    def test_percentile_inc_type7(self):
        values = [Decimal("1"), Decimal("2"), Decimal("3"), Decimal("4"), Decimal("5")]
        self.assertEqual(percentile_inc(values, Decimal("0.75")), Decimal("4"))

    def test_classification(self):
        self.assertEqual(classify(Decimal("9"), Decimal("7"), Decimal("9")), "EXTREME")
        self.assertEqual(classify(Decimal("8"), Decimal("7"), Decimal("9")), "ELEVATED")
        self.assertEqual(classify(Decimal("6"), Decimal("7"), Decimal("9")), "NORMAL")

    def test_completed_extreme_is_acute(self):
        means = {"2026-01": Decimal("1"), "2026-02": Decimal("2"), "2026-03": Decimal("10")}
        state = completed_state(means, "2026-03")
        self.assertEqual(state["stress_state"], "EXTREME")
        self.assertEqual(state["stress_phase"], "ACUTE_EXTREME")
        self.assertEqual(state["stress_vote"], -1)

    def test_partial_non_extreme_never_positive(self):
        completed = {"stress_state": "NORMAL", "stress_phase": "POST_1_3", "stress_vote": 1}
        state = apply_partial(completed, Decimal("2"), Decimal("3"), Decimal("5"))
        self.assertEqual(state["stress_vote"], 0)
        self.assertEqual(state["stress_phase"], "POST_1_3")


if __name__ == "__main__":
    unittest.main()
