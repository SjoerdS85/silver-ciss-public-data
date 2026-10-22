from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Iterable

from .common import ContractError, Observation


def previous_expected_weekday(day: date) -> date:
    candidate = day - timedelta(days=1)
    while candidate.weekday() >= 5:
        candidate -= timedelta(days=1)
    return candidate


def expected_weekdays(start: date, end: date) -> list[date]:
    if end < start:
        return []
    out: list[date] = []
    current = start
    while current <= end:
        if current.weekday() < 5:
            out.append(current)
        current += timedelta(days=1)
    return out


def missing_expected_weekdays(observations: Iterable[Observation]) -> list[date]:
    rows = sorted(observations, key=lambda x: x.day)
    if not rows:
        raise ContractError("no observations for release audit")
    present = {row.day for row in rows}
    return [d for d in expected_weekdays(rows[0].day, rows[-1].day) if d not in present]


def count_missing_expected_days(latest: date, expected_latest: date) -> int:
    if latest > expected_latest:
        raise ContractError(
            f"latest observation {latest} is newer than previous-day release contract {expected_latest}"
        )
    if latest == expected_latest:
        return 0
    return len(expected_weekdays(latest + timedelta(days=1), expected_latest))


def classify_freshness(
    missing_expected_days: int,
    *,
    degraded_after: int = 2,
    failed_after: int = 5,
) -> str:
    if missing_expected_days < 0:
        raise ContractError("negative freshness lag")
    # Governance contract: five missing expected business days already blocks.
    if missing_expected_days >= failed_after:
        return "FAILED"
    if missing_expected_days > degraded_after:
        return "DEGRADED"
    return "HEALTHY"


def parse_retrieval_timestamp(raw: str) -> datetime:
    try:
        value = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ContractError(f"invalid retrieval timestamp: {raw!r}") from exc
    if value.tzinfo is None:
        raise ContractError("retrieval timestamp must be timezone-aware")
    return value.astimezone(timezone.utc)


def audit_release(
    observations: list[Observation],
    *,
    retrieval_timestamp_utc: str,
    degraded_after: int = 2,
    failed_after: int = 5,
) -> dict:
    if not observations:
        raise ContractError("no observations for release audit")
    rows = sorted(observations, key=lambda x: x.day)
    gaps = missing_expected_weekdays(rows)
    if gaps:
        raise ContractError(
            f"missing expected weekday observations: {len(gaps)}; first={gaps[0].isoformat()}"
        )

    retrieval = parse_retrieval_timestamp(retrieval_timestamp_utc)
    expected_latest = previous_expected_weekday(retrieval.date())
    latest = rows[-1].day
    lag = count_missing_expected_days(latest, expected_latest)
    freshness = classify_freshness(
        lag,
        degraded_after=degraded_after,
        failed_after=failed_after,
    )

    return {
        "release_audit_status": "PASS" if freshness == "HEALTHY" else freshness,
        "freshness_status": freshness,
        "retrieval_timestamp_utc": retrieval.isoformat().replace("+00:00", "Z"),
        "expected_latest_observation": expected_latest.isoformat(),
        "latest_official_observation": latest.isoformat(),
        "missing_expected_days": lag,
        "historical_gap_count": 0,
        "calendar_rule": "MONDAY_TO_FRIDAY_NO_HOLIDAY_EXCLUSIONS",
    }
