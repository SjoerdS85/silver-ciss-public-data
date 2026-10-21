import unittest
from datetime import date
from decimal import Decimal

from src.common import ContractError, Observation, sha256_bytes
from src.build_publication import canonical_dataset_bytes, release_tag
from src.publish import current_pointer, require_publish_gates


class PublicationTests(unittest.TestCase):
    def test_canonical_dataset_is_deterministic(self):
        rows = [
            Observation(date(2026, 10, 20), Decimal("0.010133920731271543"), "A"),
            Observation(date(2026, 10, 19), Decimal("0.011200"), "A"),
        ]
        raw = canonical_dataset_bytes(rows)
        self.assertEqual(
            raw.decode(),
            "date,ciss\n"
            "2026-10-19,0.011200\n"
            "2026-10-20,0.010133920731271543\n",
        )
        self.assertEqual(len(sha256_bytes(raw)), 64)

    def test_release_tag_is_content_addressed(self):
        tag = release_tag(date(2026, 10, 20), "a" * 64)
        self.assertEqual(tag, "ciss-20261020-aaaaaaaaaaaa")

    def test_accepted_revision_governance_passes(self):
        require_publish_gates(
            validation_status="PASS",
            freshness_status="HEALTHY",
            release_audit_status="PASS",
            revision_governance_status="ACCEPTED_CURRENT_VINTAGE",
        )

    def test_hold_revision_blocks(self):
        with self.assertRaises(ContractError):
            require_publish_gates(
                validation_status="PASS",
                freshness_status="HEALTHY",
                release_audit_status="PASS",
                revision_governance_status="HOLD_REVISION",
            )

    def test_current_pointer_pins_release_assets(self):
        pointer = current_pointer(
            snapshot_url="https://github.com/o/r/releases/download/t/ciss_snapshot.csv",
            snapshot_manifest_url="https://github.com/o/r/releases/download/t/ciss_snapshot_manifest.json",
            sha256_dataset="a" * 64,
            snapshot_manifest_sha256="b" * 64,
            row_count=12217,
            first_observation="1980-01-03",
            last_observation="2026-10-20",
            producer_version="0.5.0-dev",
            derived_audit={"stress": {"stress_vote": 0}},
            revision_governance_status="ACCEPTED_CURRENT_VINTAGE",
            published_timestamp_utc="2026-10-21T17:23:00Z",
        )
        self.assertEqual(pointer["revision_governance_status"], "ACCEPTED_CURRENT_VINTAGE")
        self.assertEqual(pointer["valid_until_utc"], "2026-10-22T23:23:00Z")
        self.assertTrue(pointer["snapshot_url"].endswith("ciss_snapshot.csv"))


if __name__ == "__main__":
    unittest.main()
