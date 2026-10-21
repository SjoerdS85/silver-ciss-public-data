from __future__ import annotations

from datetime import datetime, timedelta, timezone

from .common import ContractError


ACCEPTED_REVISION_GOVERNANCE = {"NO_REVISIONS", "ACCEPTED_CURRENT_VINTAGE"}


def require_publish_gates(
    *,
    validation_status: str,
    freshness_status: str,
    release_audit_status: str,
    revision_governance_status: str,
) -> None:
    gates = {
        "validation_status": validation_status == "PASS",
        "freshness_status": freshness_status == "HEALTHY",
        "release_audit_status": release_audit_status == "PASS",
        "revision_governance_status": revision_governance_status in ACCEPTED_REVISION_GOVERNANCE,
    }
    failed = [name for name, ok in gates.items() if not ok]
    if failed:
        raise ContractError("publication blocked: " + ", ".join(failed))


def current_pointer(
    *,
    snapshot_url: str,
    snapshot_manifest_url: str,
    sha256_dataset: str,
    snapshot_manifest_sha256: str,
    row_count: int,
    first_observation: str,
    last_observation: str,
    producer_version: str,
    derived_audit: dict,
    revision_governance_status: str,
    published_timestamp_utc: str | None = None,
    ttl_hours: int = 30,
) -> dict:
    if revision_governance_status not in ACCEPTED_REVISION_GOVERNANCE:
        raise ContractError("current pointer blocked by revision governance")

    if published_timestamp_utc is None:
        now = datetime.now(timezone.utc).replace(microsecond=0)
    else:
        now = datetime.fromisoformat(published_timestamp_utc.replace("Z", "+00:00")).astimezone(timezone.utc)

    return {
        "schema_version": "1.2",
        "published_timestamp_utc": now.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "valid_until_utc": (now + timedelta(hours=ttl_hours)).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
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
        "revision_governance_status": revision_governance_status,
        "producer_version": producer_version,
        "derived_audit": derived_audit,
    }
