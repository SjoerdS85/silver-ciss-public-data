import unittest
from pathlib import Path


class ProductionScheduleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = Path(".github/workflows/ciss-publication.yml").read_text(encoding="utf-8")

    def test_daily_amsterdam_schedule_is_pinned(self):
        self.assertIn('cron: "17 19 * * *"', self.workflow)
        self.assertIn('timezone: "Europe/Amsterdam"', self.workflow)

    def test_schedule_runs_release_and_pages_paths(self):
        self.assertEqual(self.workflow.count("github.event_name == 'schedule' ||"), 2)

    def test_manual_confirmations_remain_required_for_dispatch(self):
        self.assertEqual(
            self.workflow.count("inputs.confirm_release_immutability_enabled == true"),
            2,
        )
        self.assertEqual(
            self.workflow.count("inputs.confirm_pages_actions_enabled == true"),
            2,
        )


if __name__ == "__main__":
    unittest.main()
