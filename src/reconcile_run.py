from __future__ import annotations

import argparse
import csv
import json
from datetime import date
from decimal import Decimal
from pathlib import Path

from .acquire import acquire_pair
from .common import ContractError, load_json, parse_decimal, parse_iso_date, sha256_bytes
from .model_stress import apply_partial, classify, completed_state, monthly_means, thresholds
from .reconcile import reconcile
from .validate import compare_full_tail, parse_csv


def month_key(day: date) -> str:
    return f"{day.year:04d}-{day.month:02d}"


def previous_month_key(day: date) -> str:
    if day.month == 1:
        return f"{day.year - 1:04d}-12"
    return f"{day.year:04d}-{day.month - 1:02d}"


def load_baseline(csv_path: str | Path, manifest_path: str | Path, contract: dict) -> dict[date, Decimal]:
    path = Path(csv_path)
    manifest = load_json(manifest_path)
    raw = path.read_bytes()
    digest = sha256_bytes(raw)
    if digest != manifest["export_sha256"]:
        raise ContractError(f"baseline SHA-256 mismatch: {digest}")
    if manifest["source_workbook_sha256"] != contract["baseline_workbook_sha256"]:
        raise ContractError("baseline workbook provenance mismatch")
    if manifest["series_key"] != contract["series_key"]:
        raise ContractError("baseline manifest series mismatch")

    rows: dict[date, Decimal] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        expected_fields = ["date", "raw_CISS", "series_code"]
        if reader.fieldnames != expected_fields:
            raise ContractError(f"unexpected baseline columns: {reader.fieldnames!r}")
        for row in reader:
            day = parse_iso_date(row["date"])
            if day in rows:
                raise ContractError(f"duplicate baseline date: {day}")
            if row["series_code"] != contract["series_key"]:
                raise ContractError(f"baseline series mismatch on {day}")
            raw_value = row["raw_CISS"]
            if "." not in raw_value or len(raw_value.rsplit(".", 1)[1]) != int(contract["baseline_comparison"]["decimal_places"]):
                raise ContractError(f"baseline value is not exact 4dp on {day}: {raw_value!r}")
            rows[day] = parse_decimal(raw_value, int(contract["baseline_comparison"]["decimal_places"]))

    dates = sorted(rows)
    if len(rows) != int(contract["baseline_expected_rows"]):
        raise ContractError(f"baseline row count {len(rows)} != {contract['baseline_expected_rows']}")
    if dates[0].isoformat() != contract["baseline_first_observation"]:
        raise ContractError("baseline first observation mismatch")
    if dates[-1].isoformat() != contract["baseline_last_observation"]:
        raise ContractError("baseline last observation mismatch")
    return rows


def history_classifications(means: dict[str, Decimal]) -> dict[str, str]:
    out: dict[str, str] = {}
    for month in sorted(means):
        th = thresholds(means, month)
        if th is not None:
            out[month] = classify(means[month], *th)
    return out


def model_impact(baseline: dict[date, Decimal], official: dict[date, Decimal], cut: date) -> dict:
    completed_before_cut = previous_month_key(cut)
    baseline_completed = [(d, v) for d, v in baseline.items() if month_key(d) <= completed_before_cut]
    official_completed = [(d, v) for d, v in official.items() if month_key(d) <= completed_before_cut]

    baseline_means = monthly_means(baseline_completed)
    official_means = monthly_means(official_completed)
    baseline_states = history_classifications(baseline_means)
    official_states = history_classifications(official_means)

    common_months = sorted(set(baseline_states) & set(official_states))
    changes = [
        {
            "month": m,
            "baseline_state": baseline_states[m],
            "official_state": official_states[m],
        }
        for m in common_months
        if baseline_states[m] != official_states[m]
    ]

    cut_month = month_key(cut)
    baseline_cut_thresholds = thresholds(baseline_means, cut_month)
    official_cut_thresholds = thresholds(official_means, cut_month)

    all_official_means = monthly_means(list(official.items()))
    cut_values = [v for d, v in official.items() if month_key(d) == cut_month]
    cut_mean = sum(cut_values, Decimal(0)) / Decimal(len(cut_values)) if cut_values else None
    cut_state = None
    if cut_mean is not None and official_cut_thresholds is not None:
        cut_state = classify(cut_mean, *official_cut_thresholds)

    latest_day = max(official)
    current_month = month_key(latest_day)
    current_values = [v for d, v in official.items() if month_key(d) == current_month]
    current_mean = sum(current_values, Decimal(0)) / Decimal(len(current_values))
    current_thresholds = thresholds(all_official_means, current_month)
    prior_month = previous_month_key(latest_day)
    previous_completed = completed_state(all_official_means, prior_month)

    if current_thresholds is None:
        partial_state = {
            "stress_state": "DATA_INSUFFICIENT",
            "stress_phase": "DATA_INSUFFICIENT",
            "stress_vote": 0,
        }
    else:
        partial_state = apply_partial(previous_completed, current_mean, *current_thresholds)

    return {
        "completed_history_last_month": completed_before_cut,
        "classification_months_compared": len(common_months),
        "classification_change_count": len(changes),
        "classification_changes": changes,
        "baseline_cut_month_thresholds": None
        if baseline_cut_thresholds is None
        else {"p75": str(baseline_cut_thresholds[0]), "p95": str(baseline_cut_thresholds[1])},
        "official_cut_month_thresholds": None
        if official_cut_thresholds is None
        else {"p75": str(official_cut_thresholds[0]), "p95": str(official_cut_thresholds[1])},
        "cut_month": cut_month,
        "cut_month_observations": len(cut_values),
        "cut_month_mean": None if cut_mean is None else str(cut_mean),
        "cut_month_state": cut_state,
        "latest_observation": latest_day.isoformat(),
        "current_month": current_month,
        "current_month_observations": len(current_values),
        "current_month_mean": str(current_mean),
        "current_month_thresholds": None
        if current_thresholds is None
        else {"p75": str(current_thresholds[0]), "p95": str(current_thresholds[1])},
        "partial_stress_state": partial_state,
    }


def write_revision_csv(path: Path, result: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "date",
                "baseline_value",
                "official_raw_value",
                "official_comparable_value",
            ],
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(result["value_diffs"])


def assess_revision_governance(
    revision_csv_path: str | Path,
    policy_path: str | Path,
    reconciliation: dict,
    impact: dict,
) -> dict:
    path = Path(revision_csv_path)
    digest = sha256_bytes(path.read_bytes())

    if reconciliation["baseline_reconciliation_status"] == "PASS":
        return {
            "status": "NO_REVISIONS",
            "revision_report_sha256": digest,
            "fingerprint_match": True,
            "publication_gate": "ELIGIBLE_FOR_NEXT_GATES",
        }

    policy = load_json(policy_path)
    accepted = policy.get("accepted_revision_fingerprint", {})
    conditions = {
        "policy_status": policy.get("status") == "ACCEPTED",
        "revision_report_sha256": digest == accepted.get("revision_report_sha256"),
        "revision_count": reconciliation["revision_count"] == accepted.get("revision_count"),
        "missing_baseline_dates": len(reconciliation["missing_baseline_dates"]) == accepted.get("missing_baseline_dates"),
        "extra_pre_cut_dates": len(reconciliation["extra_pre_cut_dates"]) == accepted.get("extra_pre_cut_dates"),
        "first_revision_date": (
            reconciliation["value_diffs"][0]["date"] if reconciliation["value_diffs"] else None
        ) == accepted.get("first_revision_date"),
        "last_revision_date": (
            reconciliation["value_diffs"][-1]["date"] if reconciliation["value_diffs"] else None
        ) == accepted.get("last_revision_date"),
        "classification_change_count": impact["classification_change_count"]
        == accepted.get("completed_month_classification_change_count"),
        "classification_months_compared": impact["classification_months_compared"]
        == accepted.get("completed_months_compared"),
    }
    match = all(conditions.values())
    return {
        "status": "ACCEPTED_CURRENT_VINTAGE" if match else "HOLD_REVISION",
        "revision_report_sha256": digest,
        "accepted_revision_report_sha256": accepted.get("revision_report_sha256"),
        "fingerprint_match": match,
        "checks": conditions,
        "publication_gate": "ELIGIBLE_FOR_NEXT_GATES" if match else "BLOCKED",
    }


def run(
    *,
    contract_path: str,
    baseline_csv: str,
    baseline_manifest: str,
    revision_policy: str,
    output_dir: str,
) -> dict:
    contract = load_json(contract_path)
    baseline_manifest_data = load_json(baseline_manifest)
    policy = load_json(revision_policy)
    if policy["accepted_model_vintage"]["baseline_csv_sha256"] != baseline_manifest_data["export_sha256"]:
        raise ContractError("revision policy baseline CSV fingerprint mismatch")
    if policy["accepted_model_vintage"]["baseline_workbook_sha256"] != baseline_manifest_data["source_workbook_sha256"]:
        raise ContractError("revision policy workbook fingerprint mismatch")

    baseline = load_baseline(baseline_csv, baseline_manifest, contract)

    out = Path(output_dir)
    acquisition = acquire_pair(contract_path, str(out / "acquisition"))
    full_raw = Path(acquisition["full"]["body_path"]).read_bytes()
    tail_raw = Path(acquisition["tail"]["body_path"]).read_bytes()

    full = parse_csv(full_raw, contract)
    tail = parse_csv(tail_raw, contract)
    compare_full_tail(full, tail)

    official = {row.day: row.value for row in full}
    cut = parse_iso_date(contract["baseline_cut_date"])
    reconciliation = reconcile(
        baseline,
        official,
        cut=cut,
        expected_rows=int(contract["baseline_expected_rows"]),
        comparison_decimals=int(contract["baseline_comparison"]["decimal_places"]),
    )

    max_abs_revision = Decimal(0)
    max_abs_revision_date = None
    for diff in reconciliation["value_diffs"]:
        delta = abs(Decimal(diff["official_comparable_value"]) - Decimal(diff["baseline_value"]))
        if delta > max_abs_revision:
            max_abs_revision = delta
            max_abs_revision_date = diff["date"]

    out.mkdir(parents=True, exist_ok=True)
    revision_path = out / "revision_report.csv"
    write_revision_csv(revision_path, reconciliation)
    impact = model_impact(baseline, official, cut)
    revision_governance = assess_revision_governance(
        revision_path,
        revision_policy,
        reconciliation,
        impact,
    )

    report = {
        "schema_version": "1.1",
        "series_key": contract["series_key"],
        "baseline_cut_date": contract["baseline_cut_date"],
        "baseline_manifest": baseline_manifest_data,
        "revision_policy": {
            "status": policy["status"],
            "accepted_at_utc": policy.get("accepted_at_utc"),
            "accepted_disposition": policy.get("accepted_disposition"),
        },
        "acquisition": {
            "full_sha256": acquisition["full"]["sha256"],
            "tail_sha256": acquisition["tail"]["sha256"],
            "retrieval_timestamp_utc": acquisition["full"]["retrieval_timestamp_utc"],
            "full_byte_count": acquisition["full"]["byte_count"],
            "tail_byte_count": acquisition["tail"]["byte_count"],
        },
        "validation": {
            "schema_adapter_status": contract["schema_adapter"]["status"],
            "full_tail_parity": "PASS",
            "official_row_count": len(full),
            "official_first_observation": full[0].day.isoformat(),
            "official_last_observation": full[-1].day.isoformat(),
        },
        "reconciliation": reconciliation,
        "revision_summary": {
            "status": reconciliation["baseline_reconciliation_status"],
            "matched_count": reconciliation["matched_count"],
            "revision_count": reconciliation["revision_count"],
            "missing_baseline_dates": len(reconciliation["missing_baseline_dates"]),
            "extra_pre_cut_dates": len(reconciliation["extra_pre_cut_dates"]),
            "first_revision_date": reconciliation["value_diffs"][0]["date"]
            if reconciliation["value_diffs"]
            else None,
            "last_revision_date": reconciliation["value_diffs"][-1]["date"]
            if reconciliation["value_diffs"]
            else None,
            "max_abs_4dp_revision": str(max_abs_revision),
            "max_abs_4dp_revision_date": max_abs_revision_date,
        },
        "model_impact": impact,
        "revision_governance": revision_governance,
        "publication_gate": revision_governance["publication_gate"],
    }

    (out / "reconciliation.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", default="config/ciss_contract_v1.json")
    parser.add_argument("--baseline-csv", default="baseline/ciss_db31_accepted_20260910.csv")
    parser.add_argument("--baseline-manifest", default="baseline/MANIFEST.json")
    parser.add_argument("--revision-policy", default="config/revision_policy_v1.json")
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    report = run(
        contract_path=args.contract,
        baseline_csv=args.baseline_csv,
        baseline_manifest=args.baseline_manifest,
        revision_policy=args.revision_policy,
        output_dir=args.output_dir,
    )
    print(json.dumps(
        {
            "reconciliation_status": report["revision_summary"]["status"],
            "revision_governance_status": report["revision_governance"]["status"],
            "revision_count": report["revision_summary"]["revision_count"],
            "classification_change_count": report["model_impact"]["classification_change_count"],
            "latest_observation": report["validation"]["official_last_observation"],
            "publication_gate": report["publication_gate"],
        },
        sort_keys=True,
    ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
