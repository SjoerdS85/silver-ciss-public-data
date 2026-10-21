from __future__ import annotations

import csv
import io
from datetime import datetime, timezone
from decimal import Decimal

from .common import ContractError, Observation, SERIES_KEY, first_present, parse_decimal, parse_iso_date

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
        day = parse_iso_date(first_present(row, adapter["date_columns"]).strip())
        if day in seen:
            raise ContractError(f"duplicate date: {day}")
        seen.add(day)
        if day > datetime.now(timezone.utc).date():
            raise ContractError(f"future date: {day}")
        value = parse_decimal(first_present(row, adapter["value_columns"]), int(contract["source_decimals"]))
        status = (first_present(row, adapter["status_columns"], required=False) or "").strip()
        if status not in set(adapter["allowed_status_values"]):
            raise ContractError(f"unknown status: {status}")
        key = first_present(row, adapter["series_key_columns"], required=False)
        if key and key.strip() != SERIES_KEY:
            raise ContractError(f"series mismatch: {key}")
        freq = first_present(row, adapter["frequency_columns"], required=False)
        if freq and freq.strip() != contract["frequency"]:
            raise ContractError("frequency mismatch")
        area = first_present(row, adapter["reference_area_columns"], required=False)
        if area and area.strip() != contract["reference_area"]:
            raise ContractError("reference area mismatch")
        unit = first_present(row, adapter["unit_columns"], required=False)
        if unit and unit.strip() != contract["unit"]:
            raise ContractError("unit mismatch")
        decimals = first_present(row, adapter["decimals_columns"], required=False)
        if decimals and int(decimals) != int(contract["source_decimals"]):
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
