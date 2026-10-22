from __future__ import annotations

import hashlib
from pathlib import Path

from .common import (
    CALCULATION_VERSION,
    MODEL_VERSION,
    MODEL_VINTAGE_DATE,
    canonical_json_bytes,
    sha256_bytes,
)


CONNECTOR_ROOT = "connector_snapshot"
ATTESTATION_NAME = "connector_attestation.json"
DATASET_NAME = "ciss_snapshot.csv"
MANIFEST_NAME = "ciss_snapshot_manifest.json"
REVISION_NAME = "revision_report.csv"


def git_blob_sha(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def build_connector_attestation(
    *,
    repository: str,
    tag: str,
    dataset_bytes: bytes,
    manifest_bytes: bytes,
    revision_bytes: bytes,
    pointer: dict,
    producer_version: str,
) -> dict:
    return {
        "schema_version": "2.0",
        "architecture": "GITHUB_CONNECTOR_SNAPSHOT_V2",
        "repository": repository,
        "tag": tag,
        "producer_version": producer_version,
        "source": pointer["source"],
        "series_key": pointer["series_key"],
        "frequency": pointer["frequency"],
        "unit": pointer["unit"],
        "calculation_version": CALCULATION_VERSION,
        "model_version": MODEL_VERSION,
        "model_vintage_date": MODEL_VINTAGE_DATE,
        "published_timestamp_utc": pointer["published_timestamp_utc"],
        "valid_until_utc": pointer["valid_until_utc"],
        "validation_status": pointer["validation_status"],
        "freshness_status": pointer["freshness_status"],
        "release_audit_status": pointer["release_audit_status"],
        "revision_governance_status": pointer["revision_governance_status"],
        "canonical": {
            "row_count": pointer["canonical_row_count"],
            "first_observation": pointer["canonical_first_observation"],
            "last_observation": pointer["canonical_last_observation"],
            "coverage_complete": pointer["canonical_coverage_complete"],
        },
        "release_assets": {
            "dataset": {
                "name": DATASET_NAME,
                "sha256": sha256_bytes(dataset_bytes),
            },
            "manifest": {
                "name": MANIFEST_NAME,
                "sha256": sha256_bytes(manifest_bytes),
            },
            "revision_report": {
                "name": REVISION_NAME,
                "sha256": sha256_bytes(revision_bytes),
            },
        },
        "tagged_files": {
            "dataset": {
                "path": f"{CONNECTOR_ROOT}/{DATASET_NAME}",
                "git_blob_sha": git_blob_sha(dataset_bytes),
            },
            "manifest": {
                "path": f"{CONNECTOR_ROOT}/{MANIFEST_NAME}",
                "git_blob_sha": git_blob_sha(manifest_bytes),
            },
            "revision_report": {
                "path": f"{CONNECTOR_ROOT}/{REVISION_NAME}",
                "git_blob_sha": git_blob_sha(revision_bytes),
            },
        },
        "derived_audit": pointer["derived_audit"],
    }


def write_connector_tree(
    *,
    output_dir: str | Path,
    attestation: dict,
    dataset_bytes: bytes,
    manifest_bytes: bytes,
    revision_bytes: bytes,
) -> dict:
    out = Path(output_dir)
    tree = out / "connector_tree" / CONNECTOR_ROOT
    tree.mkdir(parents=True, exist_ok=True)

    attestation_bytes = canonical_json_bytes(attestation)
    (tree / ATTESTATION_NAME).write_bytes(attestation_bytes)
    (tree / DATASET_NAME).write_bytes(dataset_bytes)
    (tree / MANIFEST_NAME).write_bytes(manifest_bytes)
    (tree / REVISION_NAME).write_bytes(revision_bytes)

    # The attestation is also a Release asset; the tagged-tree copy is identical.
    (out / ATTESTATION_NAME).write_bytes(attestation_bytes)

    return {
        "attestation_sha256": sha256_bytes(attestation_bytes),
        "attestation_git_blob_sha": git_blob_sha(attestation_bytes),
        "dataset_git_blob_sha": attestation["tagged_files"]["dataset"]["git_blob_sha"],
        "manifest_git_blob_sha": attestation["tagged_files"]["manifest"]["git_blob_sha"],
        "revision_git_blob_sha": attestation["tagged_files"]["revision_report"]["git_blob_sha"],
    }
