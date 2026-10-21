import copy
import json
import unittest
from datetime import date
from pathlib import Path

from src.common import ContractError, Observation
from src.release_audit import (
    audit_release,
    classify_freshness,
    missing_expected_weekdays,
)
from src.validate import compare_full_tail, parse_csv


class FailureInjectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(Path("config/ciss_contract_v1.json").read_text())

    def valid_csv(self, *, key=None, day="2026-10-20", value="0.010133920731271543") -> bytes:
        key = key or self.contract["series_key"]
        return (
            "KEY,FREQ,REF_AREA,CURRENCY,PROVIDER_FM,INSTRUMENT_FM,PROVIDER_FM_ID,DATA_TYPE_FM,"
            "TIME_PERIOD,OBS_VALUE,OBS_STATUS,DECIMALS,UNIT,UNIT_MULT\n"
            f"{key},D,U2,Z0Z,4F,EC,SS_CIN,IDX,{day},{value},A,4,PURE_NUMB,0\n"
        ).encode()

    def test_wrong_series_is_rejected(self):
        with self.assertRaises(ContractError):
            parse_csv(self.valid_csv(key="CISS.D.U2.Z0Z.4F.EC.WRONG.IDX"), self.contract)

    def test_duplicate_date_is_rejected(self):
        one = self.valid_csv().decode()
        header, row = one.splitlines()
        raw = (header + "\n" + row + "\n" + row + "\n").encode()
        with self.assertRaises(ContractError):
            parse_csv(raw, self.contract)

    def test_full_tail_race_is_rejected(self):
        full = parse_csv(self.valid_csv(day="2026-10-20"), self.contract)
        tail = parse_csv(self.valid_csv(day="2026-10-19"), self.contract)
        with self.assertRaises(ContractError):
            compare_full_tail(full, tail)

    def test_historical_weekday_gap_is_rejected(self):
        rows = [
            Observation(date(2026, 10, 16), self._d("0.01")),
            Observation(date(2026, 10, 20), self._d("0.02")),
        ]
        gaps = missing_expected_weekdays(rows)
        self.assertEqual([d.isoformat() for d in gaps], ["2026-10-19"])
        with self.assertRaises(ContractError):
            audit_release(rows, retrieval_timestamp_utc="2026-10-21T17:23:00Z")

    def test_freshness_boundaries(self):
        self.assertEqual(classify_freshness(0), "HEALTHY")
        self.assertEqual(classify_freshness(2), "HEALTHY")
        self.assertEqual(classify_freshness(3), "DEGRADED")
        self.assertEqual(classify_freshness(5), "DEGRADED")
        self.assertEqual(classify_freshness(6), "FAILED")

    def test_current_release_is_healthy(self):
        rows = [
            Observation(date(2026, 10, 19), self._d("0.01")),
            Observation(date(2026, 10, 20), self._d("0.02")),
        ]
        result = audit_release(rows, retrieval_timestamp_utc="2026-10-21T17:23:00Z")
        self.assertEqual(result["freshness_status"], "HEALTHY")
        self.assertEqual(result["missing_expected_days"], 0)

    @staticmethod
    def _d(value):
        from decimal import Decimal
        return Decimal(value)


if __name__ == "__main__":
    unittest.main()
