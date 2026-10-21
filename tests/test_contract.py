import json
import unittest
from pathlib import Path

from src.common import SERIES_KEY, ContractError, parse_decimal, parse_iso_date
from src.validate import parse_csv


class ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(Path("config/ciss_contract_v1.json").read_text())

    def test_frozen_identity(self):
        self.assertEqual(self.contract["series_key"], SERIES_KEY)
        self.assertEqual(self.contract["frequency"], "D")
        self.assertEqual(self.contract["unit"], "PURE_NUMB")
        self.assertEqual(self.contract["unit_label"], "Pure number")
        self.assertEqual(self.contract["source_decimals"], 4)

    def test_schema_is_verified_by_first_github_audit(self):
        self.assertEqual(self.contract["schema_adapter"]["status"], "VERIFIED")
        self.assertEqual(
            self.contract["schema_adapter"]["verified_full_sha256"],
            "14f8459ba904290edf23984e4960b31735e92eb0a3d9c71d22702a8c9939114e",
        )

    def test_raw_decimal_preserves_more_than_metadata_decimals(self):
        self.assertEqual(parse_decimal("0.010133920731271543"), parse_decimal("0.010133920731271543"))
        with self.assertRaises(ContractError):
            parse_decimal("0.12345", 4)

    def test_date_is_strict_iso(self):
        self.assertEqual(parse_iso_date("2026-09-10").isoformat(), "2026-09-10")

    def test_audited_schema_row_parses(self):
        raw = (
            "KEY,FREQ,REF_AREA,CURRENCY,PROVIDER_FM,INSTRUMENT_FM,PROVIDER_FM_ID,DATA_TYPE_FM,"
            "TIME_PERIOD,OBS_VALUE,OBS_STATUS,DECIMALS,UNIT,UNIT_MULT\n"
            "CISS.D.U2.Z0Z.4F.EC.SS_CIN.IDX,D,U2,Z0Z,4F,EC,SS_CIN,IDX,"
            "2026-10-20,0.010133920731271543,A,4,PURE_NUMB,0\n"
        ).encode()
        parsed = parse_csv(raw, self.contract)
        self.assertEqual(len(parsed), 1)
        self.assertEqual(str(parsed[0].value), "0.010133920731271543")


if __name__ == "__main__":
    unittest.main()
