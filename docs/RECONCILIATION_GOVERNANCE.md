# CISS reconciliation governance

The accepted DB31 CISS baseline remains the immutable model vintage for the 2026-09-12 validation cut. A later official ECB vintage may contain historical revisions.

The pipeline separates:

1. **transport/schema validity** — can the exact official ECB series be acquired and parsed;
2. **historical reconciliation** — how the current official pre-cut history differs from DB31;
3. **revision governance** — whether that exact historical revision set has been explicitly accepted for operational use.

No current-vintage value is silently written back into DB31.

## Accepted decision — 2026-10-21

Regie accepted the current official ECB vintage for ongoing operational CISS calculations while preserving DB31 unchanged as the accepted historical model vintage.

The accepted revision set is pinned by the deterministic SHA-256 of `revision_report.csv`:

`08b533af543b5d586bf6830f20d26f9d8620665994e946cfe3add2b8bda91935`

The accepted set contains 1,018 four-decimal comparison differences, no missing or extra dates, and produced zero completed-month NORMAL/ELEVATED/EXTREME classification changes across the 559 compared months.

## Mechanical rule

- no pre-cut differences: `NO_REVISIONS`;
- exact match to the accepted revision fingerprint and controls: `ACCEPTED_CURRENT_VINTAGE`;
- any different historical revision fingerprint or control mismatch: `HOLD_REVISION`.

Only `NO_REVISIONS` or `ACCEPTED_CURRENT_VINTAGE` is eligible to proceed to later production gates. A new or changed official historical revision therefore automatically returns the route to review.

This decision does not change the Silver signal-model thresholds or retroactively rewrite the 2026-09-12 research vintage.
