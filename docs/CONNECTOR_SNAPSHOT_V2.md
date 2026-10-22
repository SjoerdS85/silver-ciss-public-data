# Connector Snapshot v2 — governance record

Approved by Regie on 2026-10-22.

## Scope

This changes only the CISS transport/consumption layer. It does not change the CISS series identity, DB31 historical model vintage, prior-only expanding quantile method, stress thresholds/phase rules, Silver Signal Model v0.2, monitor evidence families, scenario ranges, or trading interpretation.

## Accepted end-to-end evidence

Scheduled Task runtime, using only the connected GitHub app:

- latest immutable v2 Release discovery: PASS;
- immutable tag file retrieval: PASS;
- full dataset materialization: PASS;
- 323,763 bytes and 12,217 unique daily observations: PASS;
- Release asset SHA-256 chain: PASS;
- tagged Git blob identity chain: PASS;
- manifest integrity: PASS;
- TTL/freshness validation: PASS;
- full-history parse: PASS;
- completed-month means: reproduced;
- prior-only expanding P75/P95: reproduced;
- stress classification: reproduced;
- exclusive stress phase: reproduced;
- numerical tolerance: within 1e-12.

Accepted Release:

`ciss-v2-20261020-20261022T080329Z-01a9f9279038`

Snapshot commit:

`a66b0493580a6335fd6b1ca9d8b89d92f99fe25d`

## Integrity evidence

```text
dataset SHA-256
01a9f927903828677dbd8349f92c9aebc43922022a3537bfc21ec5f2e529aff1

manifest SHA-256
acc328e0eadd3dcff2cf1d145a5893f563fbd5fb64c02b4d70932107c7928cd5

attestation SHA-256
1b87a73736717cb205228bbfbda3568182f5ed668f508ca964f2b3972d5bbef0

revision report SHA-256
08b533af543b5d586bf6830f20d26f9d8620665994e946cfe3add2b8bda91935
```

## Acceptance conclusion

```text
GITHUB_CONNECTOR_TASK_ROUTE=PASS
IMMUTABLE_TAG_FILE_RETRIEVAL=PASS
FULL_DATASET_MATERIALIZED=PASS
FULL_HISTORY_PARSE=PASS
DATASET_INTEGRITY_CHAIN=PASS
MANIFEST_INTEGRITY_CHAIN=PASS
TTL_FRESHNESS_CHECK=PASS
CISS_METHOD_REPRODUCTION=PASS
AUTOMATIC_CISS_ROUTE_VERIFIED=YES
```

This closes the technical CISS automatic-consumer route gate.

It does not itself authorize a GitHub production schedule, clear `RECALIBRATION_REQUIRED`, or reactivate either Silver monitor. Those remain separate Regie decisions.
