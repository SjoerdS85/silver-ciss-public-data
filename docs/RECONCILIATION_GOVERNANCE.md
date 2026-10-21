# CISS reconciliation governance

The accepted DB31 CISS baseline is an immutable model vintage for the 2026-09-12 validation cut. A later official ECB vintage may contain historical revisions.

The pipeline therefore separates two questions:

1. **Transport and schema validity** — can the exact official ECB series be acquired and parsed under the frozen contract?
2. **Vintage reconciliation** — does the current official history equal the accepted DB31 vintage after the explicit four-decimal comparison normalization?

A current-vintage value difference is never silently written back into the DB31 baseline. It is emitted into `revision_report.csv`, retained with acquisition hashes, and evaluated for model impact.

## Status rules

- no date/value differences through the cut: `PASS`;
- historical value differences through the cut: `HOLD_REVISION`;
- missing/extra dates, schema/series failure, invalid baseline hash, or full/tail inconsistency: fail the audit before trusted publication;
- `HOLD_REVISION` blocks the trusted current publication pointer until Regie explicitly disposes of the revision evidence.

## Model-impact check

For each run the audit independently recomputes monthly means and prior-only expanding P75/P95 thresholds for the accepted baseline and the current official vintage. It counts historical NORMAL/ELEVATED/EXTREME classification changes and separately reports the current cut-month and partial-current-month stress state.

No result from this audit changes the Silver signal model thresholds or monitor governance by itself.
