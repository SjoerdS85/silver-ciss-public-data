import json
import unittest
from pathlib import Path

from src.common import SERIES_KEY, ContractError, parse_decimal, parse_iso_date


class ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(Path("config/ciss_contract_v1.json").read_text())

    def test_frozen_identity(self):
        self.assertEqual(self.contract["series_key"], SERIES_KEY)
        self.assertEqual(self.contract["frequency"], "D")
        self.assertEqual(self.contract["unit"], "Pure number")
        self.assertEqual(self.contract["source_decimals"], 4)

    def test_schema_starts_unverified(self):
        self.assertNotEqual(self.contract["schema_adapter"]["status"], "VERIFIED")

    def test_decimal_precision_rejects_five_places(self):
        with self.assertRaises(ContractError):
            parse_decimal("0.12345", 4)

    def test_date_is_strict_iso(self):
        self.assertEqual(parse_iso_date("2026-09-10").isoformat(), "2026-09-10")


if __name__ == "__main__":
    unittest.main()
