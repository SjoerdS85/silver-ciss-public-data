import csv
import hashlib
import unittest
from pathlib import Path


BASELINE = Path("baseline/ciss_db31_accepted_20260910.csv")
EXPECTED_SHA256 = "40e1d3d78b743b8f4e69b3a50d1f620b2e3c35156481b69fe346e571369c4d34"
EXPECTED_ROWS = 12189
EXPECTED_SERIES = "CISS.D.U2.Z0Z.4F.EC.SS_CIN.IDX"


class BaselineExportFileTests(unittest.TestCase):
    def test_controlled_export_contract(self):
        self.assertTrue(BASELINE.exists(), "controlled DB31 baseline CSV is missing")
        raw = BASELINE.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), EXPECTED_SHA256)

        with BASELINE.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))

        self.assertEqual(len(rows), EXPECTED_ROWS)
        self.assertEqual(rows[0]["date"], "1980-01-03")
        self.assertEqual(rows[-1]["date"], "2026-09-10")
        self.assertTrue(all(row["series_code"] == EXPECTED_SERIES for row in rows))
        self.assertTrue(all(len(row["raw_CISS"].split(".")[-1]) == 4 for row in rows))


if __name__ == "__main__":
    unittest.main()
