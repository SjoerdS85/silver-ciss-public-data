from __future__ import annotations

from datetime import datetime, timedelta, timezone

from .common import ContractError


def require_publish_gates(validation_status: str, freshness_status: str, release_audit_status: str, reconciliation_status: str) -> None:
    gates = {
        "validation_status": validation_status == "PASS",
        "freshness_status": freshness_status == "HEALTHY",
        "release_audit_status": release_audit_status == "PASS",
        "baseline_reconciliation_status": reconciliation_status == "PASS",
    }
    failed = [name for name, ok in gates.items() if not ok]
    if failed:
        raise ContractError("publication blocked: " + ", ".join(failed))


def current_pointer(*, snapshot_url: str, snapshot_manifest_url: str, sha256_dataset: str, snapshot_manifest_sha256: str, row_count: int, first_observation: str, last_observation: str, producer_version: str, derived_audit: dict, ttl_hours: int = 30) -> dict:
    now = datetime.now(timezone.utc).replace(microsecond=0)
    return {
        "schema_version": "1.1",
        "published_timestamp_utc": now.isoformat().replace("+00:00", "Z"),
        "valid_until_utc": (now + timedelta(hours=ttl_hours)).isoformat().replace("+00:00", "Z"),
        "snapshot_url": snapshot_url,
        "snapshot_manifest_url": snapshot_manifest_url,
        "sha256_dataset": sha256_dataset,
        "snapshot_manifest_sha256": snapshot_manifest_sha256,
        "canonical_row_count": row_count,
        "canonical_first_observation": first_observation,
        "canonical_last_observation": last_observation,
        "canonical_coverage_complete": True,
        "source": "ECB_OFFICIAL",
        "series_key": "CISS.D.U2.Z0Z.4F.EC.SS_CIN.IDX",
        "frequency": "D",
        "unit": "Pure number",
        "validation_status": "PASS",
        "freshness_status": "HEALTHY",
        "release_audit_status": "PASS",
        "baseline_reconciliation_status": "PASS",
        "producer_version": producer_version,
        "derived_audit": derived_audit,
    }
