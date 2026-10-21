from __future__ import annotations

from datetime import date
from decimal import Decimal

from .common import ContractError


def reconcile(baseline: dict[date, Decimal], official: dict[date, Decimal], *, cut: date, expected_rows: int = 12189) -> dict:
    if len(baseline) != expected_rows:
        raise ContractError(f"baseline row count {len(baseline)} != {expected_rows}")
    baseline_dates = set(baseline)
    official_pre_cut = {d for d in official if d <= cut}
    missing = sorted(baseline_dates - official_pre_cut)
    extra = sorted(official_pre_cut - baseline_dates)
    diffs = [
        {"date": d.isoformat(), "baseline_value": str(baseline[d]), "official_value": str(official[d])}
        for d in sorted(baseline_dates & official_pre_cut)
        if baseline[d] != official[d]
    ]
    new_dates = sorted(d for d in official if d > cut)
    return {
        "baseline_reconciliation_status": "PASS" if not missing and not extra and not diffs else "HOLD_REVISION",
        "matched_count": len(baseline_dates & official_pre_cut) - len(diffs),
        "missing_baseline_dates": [d.isoformat() for d in missing],
        "extra_pre_cut_dates": [d.isoformat() for d in extra],
        "value_diffs": diffs,
        "new_dates": [d.isoformat() for d in new_dates],
        "first_new_date": new_dates[0].isoformat() if new_dates else None,
        "last_new_date": new_dates[-1].isoformat() if new_dates else None,
    }
