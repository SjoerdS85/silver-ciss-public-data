# silver-ciss-public-data

Public reproducible CISS acquisition and publication layer for Silver Market Research.

## Purpose

This repository is the free/public production route for the exact ECB CISS series:

`CISS.D.U2.Z0Z.4F.EC.SS_CIN.IDX`

Primary source: official ECB Data API.

The accepted signal-model definitions, CISS calculation rules, source identity, DB31 model vintage and Regie gates are unchanged.

## Verified producer state

- GitHub-hosted official ECB transport: PASS.
- Exact live ECB CSV schema: VERIFIED.
- Controlled DB31 baseline: hashed and CI-verified.
- Current official historical revision fingerprint: accepted for operational CISS; DB31 remains the immutable accepted 2026-09-12 model vintage.
- Release calendar/freshness audit: PASS.
- Exact governance boundary: five missing expected business days = FAILED/blocking.
- Main branch ruleset: active; PR plus `test` status check required.
- GitHub Release immutability: VERIFIED on a real release.
- GitHub Pages: VERIFIED on real deployment and independent public read-back.
- Direct HTTPS from ChatGPT Scheduled Task runtime: FAILED DNS on GitHub hosts on 2026-10-22.
- GitHub connector from Scheduled Task runtime: release metadata/repository file retrieval PASS.
- Full connector-snapshot Task consumer: pending v2 snapshot publication and end-to-end probe.
- Scheduled production: disabled.
- Silver monitors: outside this repository and remain subject to separate Regie approval.

## First verified v1 publication

- release tag: `ciss-20261020-01a9f9279038`
- dataset SHA-256: `01a9f927903828677dbd8349f92c9aebc43922022a3537bfc21ec5f2e529aff1`
- manifest SHA-256: `41fcf0adc4f349140059cbf292854d9e632018fe07002a93c97025d06f115cbb`
- revision report SHA-256: `08b533af543b5d586bf6830f20d26f9d8620665994e946cfe3add2b8bda91935`
- canonical rows: 12,217
- first observation: 1980-01-03
- last observation: 2026-10-20

## Connector Snapshot Architecture v2

The v2 consumer route avoids direct Scheduled Task DNS/HTTP.

A successful manual publication run creates:

1. the validated canonical full-history dataset;
2. the immutable snapshot manifest;
3. the DB31 revision report;
4. a connector attestation containing release SHA-256 values and Git blob SHAs;
5. an orphan/data-only Git commit containing those four files under `connector_snapshot/`;
6. an immutable GitHub Release whose immutable tag points to that data-only commit;
7. the same four objects as immutable Release assets;
8. the existing GitHub Pages read-only copy for independent external audit.

The Scheduled Task can discover the latest immutable release through the connected GitHub app, use its immutable tag as `ref`, retrieve the tagged text files through the connector, compare connector-reported Git blob SHAs with the attestation, compare attested SHA-256 values with immutable Release asset digests, parse the full dataset and execute the frozen CISS calculation rules itself.

Release notes are not part of the integrity chain.

## Remaining activation gates

Before automatic production and monitor reactivation:

1. publish one real v2 connector snapshot;
2. verify immutable tag -> data-only commit and tagged-tree read-back;
3. run a Scheduled Task connector probe that materializes the full tagged dataset and manifest;
4. reproduce completed-month means, prior-only P75/P95 and stress phase in the actual Task runtime;
5. verify TTL/freshness and fail-closed behavior;
6. only then decide `AUTOMATIC_CISS_ROUTE_VERIFIED=YES`;
7. separately decide production schedule and monitor reactivation.

Until then, scheduled production remains disabled and fail-closed.
