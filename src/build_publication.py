from __future__ import annotations

import argparse
import csv
import io
import json
import os
from pathlib import Path

from .acquire import acquire_pair
from .common import ContractError, Observation, canonical_json_bytes, load_json, parse_iso_date, sha256_bytes
from .publish import current_pointer, require_publish_gates
from .reconcile import reconcile
from .reconcile_run import assess_revision_governance, load_baseline, model_impact, write_revision_csv
from .release_audit import audit_release
from .validate import compare_full_tail, parse_csv


def canonical_dataset_bytes(rows: list[Observation]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(["date", "ciss"])
    for row in sorted(rows, key=lambda x: x.day):
        writer.writerow([row.day.isoformat(), format(row.value, "f")])
    return stream.getvalue().encode("utf-8")


def release_tag(latest_observation, dataset_sha256: str) -> str:
    return f"ciss-{latest_observation.strftime('%Y%m%d')}-{dataset_sha256[:12]}"


def build_publication(
    *,
    repository: str,
    output_dir: str,
    contract_path: str = "config/ciss_contract_v1.json",
    release_policy_path: str = "config/ciss_release_policy_v1.json",
    revision_policy_path: str = "config/revision_policy_v1.json",
    baseline_csv_path: str = "baseline/ciss_db31_accepted_20260910.csv",
    baseline_manifest_path: str = "baseline/MANIFEST.json",
    version_path: str = "VERSION",
) -> dict:
    if "/" not in repository:
        raise ContractError("repository must be owner/name")

    contract = load_json(contract_path)
    release_policy = load_json(release_policy_path)
    revision_policy = load_json(revision_policy_path)
    baseline_manifest = load_json(baseline_manifest_path)
    baseline = load_baseline(baseline_csv_path, baseline_manifest_path, contract)

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    acquisition = acquire_pair(contract_path, str(out / "acquisition"))

    full_raw = Path(acquisition["full"]["body_path"]).read_bytes()
    tail_raw = Path(acquisition["tail"]["body_path"]).read_bytes()
    full = parse_csv(full_raw, contract)
    tail = parse_csv(tail_raw, contract)
    compare_full_tail(full, tail)

    release = audit_release(
        full,
        retrieval_timestamp_utc=acquisition["full"]["retrieval_timestamp_utc"],
        degraded_after=release_policy["freshness"]["healthy_max_missing_expected_days"],
        failed_after=release_policy["freshness"]["failed_above_missing_expected_days"],
    )

    official = {row.day: row.value for row in full}
    cut = parse_iso_date(contract["baseline_cut_date"])
    reconciliation = reconcile(
        baseline,
        official,
        cut=cut,
        expected_rows=int(contract["baseline_expected_rows"]),
        comparison_decimals=int(contract["baseline_comparison"]["decimal_places"]),
    )
    revision_path = out / "revision_report.csv"
    write_revision_csv(revision_path, reconciliation)
    impact = model_impact(baseline, official, cut)
    revision_governance = assess_revision_governance(
        revision_path,
        revision_policy_path,
        reconciliation,
        impact,
    )

    require_publish_gates(
        validation_status="PASS",
        freshness_status=release["freshness_status"],
        release_audit_status=release["release_audit_status"],
        revision_governance_status=revision_governance["status"],
    )

    dataset = canonical_dataset_bytes(full)
    dataset_sha = sha256_bytes(dataset)
    latest = full[-1].day
    tag = release_tag(latest, dataset_sha)
    producer_version = Path(version_path).read_text(encoding="utf-8").strip()

    snapshot_path = out / "ciss_snapshot.csv"
    snapshot_path.write_bytes(dataset)

    snapshot_manifest = {
        "schema_version": "1.0",
        "tag": tag,
        "producer_version": producer_version,
        "source": "ECB_OFFICIAL",
        "series_key": contract["series_key"],
        "frequency": contract["frequency"],
        "unit": contract["unit_label"],
        "generated_from_retrieval_timestamp_utc": acquisition["full"]["retrieval_timestamp_utc"],
        "canonical_dataset": {
            "file_name": snapshot_path.name,
            "sha256": dataset_sha,
            "byte_count": len(dataset),
            "row_count": len(full),
            "first_observation": full[0].day.isoformat(),
            "last_observation": full[-1].day.isoformat(),
        },
        "source_evidence": {
            "full_sha256": acquisition["full"]["sha256"],
            "tail_sha256": acquisition["tail"]["sha256"],
            "full_tail_parity": "PASS",
        },
        "release_audit": release,
        "revision_governance": {
            "status": revision_governance["status"],
            "revision_report_sha256": revision_governance["revision_report_sha256"],
            "fingerprint_match": revision_governance["fingerprint_match"],
            "accepted_at_utc": revision_policy.get("accepted_at_utc"),
        },
        "model_audit": {
            "classification_months_compared": impact["classification_months_compared"],
            "classification_change_count": impact["classification_change_count"],
            "cut_month": impact["cut_month"],
            "cut_month_state": impact["cut_month_state"],
            "current_month": impact["current_month"],
            "partial_stress_state": impact["partial_stress_state"],
        },
        "baseline_provenance": {
            "baseline_csv_sha256": baseline_manifest["export_sha256"],
            "baseline_workbook_sha256": baseline_manifest["source_workbook_sha256"],
        },
    }

    manifest_path = out / "ciss_snapshot_manifest.json"
    manifest_bytes = canonical_json_bytes(snapshot_manifest)
    manifest_path.write_bytes(manifest_bytes)
    manifest_sha = sha256_bytes(manifest_bytes)

    release_base = f"https://github.com/{repository}/releases/download/{tag}"
    pointer = current_pointer(
        snapshot_url=f"{release_base}/{snapshot_path.name}",
        snapshot_manifest_url=f"{release_base}/{manifest_path.name}",
        sha256_dataset=dataset_sha,
        snapshot_manifest_sha256=manifest_sha,
        row_count=len(full),
        first_observation=full[0].day.isoformat(),
        last_observation=full[-1].day.isoformat(),
        producer_version=producer_version,
        derived_audit={
            "stress": impact["partial_stress_state"],
            "revision_report_sha256": revision_governance["revision_report_sha256"],
        },
        revision_governance_status=revision_governance["status"],
        published_timestamp_utc=acquisition["full"]["retrieval_timestamp_utc"],
        ttl_hours=int(contract["current_ttl_hours"]),
    )

    site = out / "site" / "ciss" / "v1"
    site.mkdir(parents=True, exist_ok=True)
    (site / "ciss_current.csv").write_bytes(dataset)
    (site / "ciss_current_manifest.json").write_bytes(manifest_bytes)
    (site / "current.json").write_bytes(canonical_json_bytes(pointer))

    (out / "tag.txt").write_text(tag + "\n", encoding="utf-8")
    notes = (
        f"Official ECB New CISS snapshot through {latest.isoformat()}.\n\n"
        f"Dataset SHA-256: {dataset_sha}\n"
        f"Manifest SHA-256: {manifest_sha}\n"
        f"Revision governance: {revision_governance['status']}\n"
        f"Freshness: {release['freshness_status']}\n"
    )
    (out / "release_notes.md").write_text(notes, encoding="utf-8")

    summary = {
        "tag": tag,
        "dataset_sha256": dataset_sha,
        "manifest_sha256": manifest_sha,
        "row_count": len(full),
        "first_observation": full[0].day.isoformat(),
        "last_observation": full[-1].day.isoformat(),
        "freshness_status": release["freshness_status"],
        "revision_governance_status": revision_governance["status"],
        "publication_gate": "PASS",
    }
    (out / "publication_summary.json").write_bytes(canonical_json_bytes(summary))
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", default=os.environ.get("GITHUB_REPOSITORY", ""))
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    summary = build_publication(repository=args.repository, output_dir=args.output_dir)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
