from __future__ import annotations

import csv
import io
from datetime import datetime, timezone
from decimal import Decimal

from .common import ContractError, Observation, SERIES_KEY, first_present, parse_decimal, parse_iso_date


def _required(row: dict[str, str], adapter: dict, name: str) -> str:
    return first_present(row, adapter[name], required=True).strip()


def parse_csv(raw: bytes, contract: dict, *, permit_unverified_adapter: bool = False) -> list[Observation]:
    adapter = contract["schema_adapter"]
    if adapter.get("status") != "VERIFIED" and not permit_unverified_adapter:
        raise ContractError("schema adapter not VERIFIED")

    text = raw.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames:
        raise ContractError("CSV has no header")

    rows: list[Observation] = []
    seen = set()

    for row in reader:
        day = parse_iso_date(_required(row, adapter, "date_columns"))
        if day in seen:
            raise ContractError(f"duplicate date: {day}")
        seen.add(day)
        if day > datetime.now(timezone.utc).date():
            raise ContractError(f"future date: {day}")

        # Preserve the exact official decimal representation. DECIMALS is
        # validated as metadata separately and is not treated as a storage cap.
        value = parse_decimal(_required(row, adapter, "value_columns"))

        status = _required(row, adapter, "status_columns")
        if status not in set(adapter["allowed_status_values"]):
            raise ContractError(f"unknown status: {status}")

        checks = [
            ("series", _required(row, adapter, "series_key_columns"), SERIES_KEY),
            ("frequency", _required(row, adapter, "frequency_columns"), contract["frequency"]),
            ("reference area", _required(row, adapter, "reference_area_columns"), contract["reference_area"]),
            ("currency", _required(row, adapter, "currency_columns"), contract["currency_code"]),
            ("provider", _required(row, adapter, "provider_columns"), contract["provider_code"]),
            ("instrument", _required(row, adapter, "instrument_columns"), contract["instrument_code"]),
            ("provider id", _required(row, adapter, "provider_id_columns"), contract["provider_id_code"]),
            ("data type", _required(row, adapter, "data_type_columns"), contract["data_type_code"]),
            ("unit", _required(row, adapter, "unit_columns"), contract["unit"]),
        ]
        for label, observed, expected in checks:
            if observed != expected:
                raise ContractError(f"{label} mismatch: {observed!r} != {expected!r}")

        if int(_required(row, adapter, "unit_multiplier_columns")) != int(contract["unit_multiplier"]):
            raise ContractError("UNIT_MULT mismatch")
        if int(_required(row, adapter, "decimals_columns")) != int(contract["source_decimals"]):
            raise ContractError("DECIMALS mismatch")

        rows.append(Observation(day, value, status))

    rows.sort(key=lambda x: x.day)
    if not rows:
        raise ContractError("no observations")
    for a, b in zip(rows, rows[1:]):
        if b.day <= a.day:
            raise ContractError("dates not strictly increasing")
    return rows


def compare_full_tail(full: list[Observation], tail: list[Observation]) -> None:
    if len(tail) > len(full):
        raise ContractError("tail longer than full")
    expected = full[-len(tail):]
    if [(x.day, x.value, x.status) for x in expected] != [(x.day, x.value, x.status) for x in tail]:
        raise ContractError("full/tail release race")


def percentile_inc(values: list[Decimal], p: Decimal) -> Decimal:
    if not values:
        raise ContractError("empty percentile input")
    xs = sorted(values)
    if len(xs) == 1:
        return xs[0]
    rank = Decimal(len(xs) - 1) * p
    lo = int(rank)
    hi = min(lo + 1, len(xs) - 1)
    weight = rank - Decimal(lo)
    return xs[lo] + (xs[hi] - xs[lo]) * weight
