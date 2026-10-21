from __future__ import annotations

from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from .common import ContractError


def comparable_value(value: Decimal, decimal_places: int = 4) -> Decimal:
    quantum = Decimal(1).scaleb(-decimal_places)
    return value.quantize(quantum, rounding=ROUND_HALF_UP)


def reconcile(
    baseline: dict[date, Decimal],
    official: dict[date, Decimal],
    *,
    cut: date,
    expected_rows: int = 12189,
    comparison_decimals: int = 4,
) -> dict:
    if len(baseline) != expected_rows:
        raise ContractError(f"baseline row count {len(baseline)} != {expected_rows}")

    baseline_dates = set(baseline)
    official_pre_cut = {d for d in official if d <= cut}
    missing = sorted(baseline_dates - official_pre_cut)
    extra = sorted(official_pre_cut - baseline_dates)

    diffs = []
    matched = 0
    for d in sorted(baseline_dates & official_pre_cut):
        raw = official[d]
        comparable = comparable_value(raw, comparison_decimals)
        if baseline[d] == comparable:
            matched += 1
        else:
            diffs.append(
                {
                    "date": d.isoformat(),
                    "baseline_value": str(baseline[d]),
                    "official_raw_value": str(raw),
                    "official_comparable_value": str(comparable),
                }
            )

    new_dates = sorted(d for d in official if d > cut)
    return {
        "baseline_reconciliation_status": "PASS" if not missing and not extra and not diffs else "HOLD_REVISION",
        "comparison_decimals": comparison_decimals,
        "comparison_rounding": "ROUND_HALF_UP",
        "matched_count": matched,
        "revision_count": len(diffs),
        "missing_baseline_dates": [d.isoformat() for d in missing],
        "extra_pre_cut_dates": [d.isoformat() for d in extra],
        "value_diffs": diffs,
        "new_dates": [d.isoformat() for d in new_dates],
        "first_new_date": new_dates[0].isoformat() if new_dates else None,
        "last_new_date": new_dates[-1].isoformat() if new_dates else None,
    }
