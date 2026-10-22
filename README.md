# silver-ciss-public-data

Public reproducible CISS acquisition and publication layer for Silver Market Research.

## Purpose

This repository is the free/public production route for the exact ECB CISS series:

`CISS.D.U2.Z0Z.4F.EC.SS_CIN.IDX`

Primary source: official ECB Data API.

The accepted signal-model definitions, CISS calculation rules, source identity, DB31 model vintage and Regie gates are unchanged.

## Verified state

- GitHub-hosted official ECB transport: PASS.
- Exact live ECB CSV schema: VERIFIED.
- Controlled DB31 baseline: hashed and CI-verified.
- Current official historical revision fingerprint: accepted for operational CISS; DB31 remains the immutable accepted 2026-09-12 model vintage.
- Release calendar/freshness audit: PASS.
- Exact governance boundary: five missing expected business days = FAILED/blocking.
- Main branch ruleset: active; PR plus `test` status check required.
- GitHub Release immutability: VERIFIED.
- GitHub Pages/public read-back: VERIFIED.
- Direct HTTPS from ChatGPT Scheduled Task runtime: FAILED DNS on GitHub hosts on 2026-10-22.
- GitHub connector from Scheduled Task runtime: FULL END-TO-END PASS.
- Full 323,763-byte / 12,217-row connector snapshot materialization: PASS.
- Release asset SHA-256 + tagged Git blob integrity chain: PASS.
- TTL/freshness validation: PASS.
- CISS completed-month / prior-only P75/P95 / stress-state / stress-phase reproduction: PASS within 1e-12.
- `AUTOMATIC_CISS_ROUTE_VERIFIED=YES`.
- Scheduled production: still disabled pending separate Regie go-live.
- Silver Guardrail Watch and Full Monitor: still paused pending separate reactivation decision.

## Accepted Connector Snapshot v2 release

- release tag: `ciss-v2-20261020-20261022T080329Z-01a9f9279038`
- snapshot commit: `a66b0493580a6335fd6b1ca9d8b89d92f99fe25d`
- immutable: `true`
- dataset SHA-256: `01a9f927903828677dbd8349f92c9aebc43922022a3537bfc21ec5f2e529aff1`
- manifest SHA-256: `acc328e0eadd3dcff2cf1d145a5893f563fbd5fb64c02b4d70932107c7928cd5`
- attestation SHA-256: `1b87a73736717cb205228bbfbda3568182f5ed668f508ca964f2b3972d5bbef0`
- revision report SHA-256: `08b533af543b5d586bf6830f20d26f9d8620665994e946cfe3add2b8bda91935`
- dataset Git blob SHA: `9bd77663c8e861ca880e739023f6f37e985f6dac`
- manifest Git blob SHA: `76a63525dc673110b74dba8f00f08cce7ca923ff`
- attestation Git blob SHA: `3b8b3328ed02d23bce1175cd61e92872ac84494b`
- canonical rows: 12,217
- first observation: 1980-01-03
- last observation: 2026-10-20

## Connector Snapshot Architecture v2

The Scheduled Task does not depend on direct public DNS/HTTP. It discovers the latest immutable v2 release through the connected GitHub app, uses the immutable tag as `ref`, retrieves the tagged attestation, manifest and full canonical CSV, verifies Git blob identities against the attestation, verifies SHA-256 values against immutable Release asset digests, validates freshness/TTL and series identity, then executes the frozen CISS method itself.

Release notes are not part of the integrity chain.

## Remaining activation gates

The CISS transport route is technically verified. Remaining steps are operational/governance decisions:

1. authorize a production schedule;
2. add the GitHub Actions scheduled trigger;
3. observe at least the first scheduled publication and connector consumption cycle;
4. separately decide whether `RECALIBRATION_REQUIRED` can be cleared;
5. separately reactivate Guardrail Watch and/or Full Monitor under the accepted monitor specification.

Until the production schedule is authorized, scheduled publication remains disabled.
