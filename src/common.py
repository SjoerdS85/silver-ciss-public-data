from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Mapping, Sequence

SERIES_KEY = "CISS.D.U2.Z0Z.4F.EC.SS_CIN.IDX"
BASELINE_WORKBOOK_SHA256 = "e5efd6d729cca0d2d79f49b9a2262db3517a595f9eeae68ddda58a85579fa151"
CALCULATION_VERSION = "CISS_EXPANDING_REALTIME_LIKE_V0_2"
MODEL_VERSION = "50_Silver_Signal_Model.md v0.2"
MODEL_VINTAGE_DATE = "2026-09-12"

class ContractError(RuntimeError):
    pass

@dataclass(frozen=True)
class Observation:
    day: date
    value: Decimal
    status: str = ""
    series_key: str = SERIES_KEY

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def canonical_json_bytes(payload: Mapping) -> bytes:
    return (json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")

def load_json(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))

def parse_iso_date(raw: str) -> date:
    try:
        value = date.fromisoformat(raw)
    except ValueError as exc:
        raise ContractError(f"invalid ISO date: {raw!r}") from exc
    if value.isoformat() != raw:
        raise ContractError(f"date is not canonical YYYY-MM-DD: {raw!r}")
    return value

def parse_decimal(raw: str, max_decimal_places: int = 4) -> Decimal:
    text = raw.strip()
    if not text or "e" in text.lower():
        raise ContractError(f"invalid decimal representation: {raw!r}")
    try:
        value = Decimal(text)
    except InvalidOperation as exc:
        raise ContractError(f"invalid decimal: {raw!r}") from exc
    if not value.is_finite():
        raise ContractError("non-finite decimal")
    if max(0, -value.as_tuple().exponent) > max_decimal_places:
        raise ContractError(f"more than {max_decimal_places} decimal places: {raw!r}")
    return value

def decimal_text(value: Decimal) -> str:
    text = format(value, "f")
    return text.rstrip("0").rstrip(".") if "." in text else text

def first_present(row: Mapping[str, str], candidates: Sequence[str], required: bool = True) -> str | None:
    for key in candidates:
        if key in row and row[key] is not None:
            return row[key]
    if required:
        raise ContractError(f"missing required column; tried {list(candidates)}")
    return None
