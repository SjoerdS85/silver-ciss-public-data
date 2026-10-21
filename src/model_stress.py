from __future__ import annotations

from collections import defaultdict
from datetime import date
from decimal import Decimal

from .common import ContractError
from .validate import percentile_inc

ALLOWED_PHASES = {"ACUTE_EXTREME", "POST_1_3", "POST_4_6", "NONE", "DATA_INSUFFICIENT"}


def month_key(day: date) -> str:
    return f"{day.year:04d}-{day.month:02d}"


def monthly_means(rows: list[tuple[date, Decimal]]) -> dict[str, Decimal]:
    buckets = defaultdict(list)
    for day, value in rows:
        buckets[month_key(day)].append(value)
    return {m: sum(vs, Decimal(0)) / Decimal(len(vs)) for m, vs in sorted(buckets.items())}


def thresholds(means: dict[str, Decimal], month: str) -> tuple[Decimal, Decimal] | None:
    prior = [v for m, v in means.items() if m < month]
    if not prior:
        return None
    return percentile_inc(prior, Decimal("0.75")), percentile_inc(prior, Decimal("0.95"))


def classify(mean: Decimal, p75: Decimal, p95: Decimal) -> str:
    if mean >= p95:
        return "EXTREME"
    if mean >= p75:
        return "ELEVATED"
    return "NORMAL"


def completed_state(means: dict[str, Decimal], month: str) -> dict:
    th = thresholds(means, month)
    if month not in means or th is None:
        return {"stress_state": "DATA_INSUFFICIENT", "stress_phase": "DATA_INSUFFICIENT", "stress_vote": 0}
    state = classify(means[month], *th)
    if state == "EXTREME":
        return {"stress_state": state, "stress_phase": "ACUTE_EXTREME", "stress_vote": -1}
    months = sorted(means)
    extreme = []
    for m in months:
        mt = thresholds(means, m)
        if mt and classify(means[m], *mt) == "EXTREME":
            extreme.append(m)
    previous = [m for m in extreme if m < month]
    if not previous:
        phase = "NONE"
    else:
        delta = months.index(month) - months.index(previous[-1])
        phase = "POST_1_3" if 1 <= delta <= 3 else "POST_4_6" if 4 <= delta <= 6 else "NONE"
    if phase not in ALLOWED_PHASES:
        raise ContractError("invalid phase")
    return {"stress_state": state, "stress_phase": phase, "stress_vote": 1 if phase in {"POST_1_3", "POST_4_6"} else 0}


def apply_partial(completed: dict, partial_mean: Decimal, p75: Decimal, p95: Decimal) -> dict:
    state = classify(partial_mean, p75, p95)
    if state == "EXTREME":
        return {"stress_state": "EXTREME", "stress_phase": "ACUTE_EXTREME", "stress_vote": -1}
    return {"stress_state": state, "stress_phase": completed["stress_phase"], "stress_vote": 0}
