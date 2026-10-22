# silver-ciss-public-data

Public reproducible CISS acquisition and publication layer for Silver Market Research.

## Purpose

This repository is the free/public production route for the exact ECB CISS series:

CISS.D.U2.Z0Z.4F.EC.SS_CIN.IDX

Primary source: official ECB Data API.

It replaces only the external AWS/S3 publication layer that was previously proposed. The accepted signal-model definitions, CISS calculation rules, source identity, baseline reconciliation requirements and Regie approval gates remain unchanged.

## Current verified state

- GitHub-hosted official ECB transport: PASS.
- Exact live ECB CSV schema: VERIFIED.
- Controlled DB31 baseline: committed, hashed and CI-verified.
- Current official historical revision fingerprint: accepted for operational CISS; DB31 remains the immutable accepted 2026-09-12 model vintage.
- Release calendar and freshness audit: PASS.
- Failure-injection tests: active.
- Main branch ruleset: active; PR plus test status check required.
- GitHub release immutability: VERIFIED on real release.
- GitHub Pages: VERIFIED on real deployment and independent public read-back.
- Public Pages dataset and immutable Release dataset: byte-identical.
- Production route: VERIFIED.
- Scheduled production: disabled pending Regie go-live.
- ChatGPT Scheduled Task consumer route: not yet verified.
- Silver monitor reactivation: outside this repository and requires separate Regie approval.

## Verified publication

First validated publication:
- release tag: ciss-20261020-01a9f9279038
- dataset SHA-256: 01a9f927903828677dbd8349f92c9aebc43922022a3537bfc21ec5f2e529aff1
- manifest SHA-256: 41fcf0adc4f349140059cbf292854d9e632018fe07002a93c97025d06f115cbb
- revision report SHA-256: 08b533af543b5d586bf6830f20d26f9d8620665994e946cfe3add2b8bda91935
- canonical rows: 12,217
- first observation: 1980-01-03
- last observation: 2026-10-20

## Free production architecture

Official ECB CISS
-> GitHub Actions
-> schema + freshness + DB31/revision governance
-> content-addressed immutable GitHub Release
+ GitHub Pages current read-only surface
-> future ChatGPT Scheduled Task

No AWS credentials, long-lived cloud credentials, private project data or secrets belong in this repository.

## Remaining activation gates

Before automatic production and monitor reactivation:
1. Regie production go-live decision;
2. add the scheduled production trigger only after that decision;
3. run a ChatGPT Scheduled Task consumer probe against the public read-only route;
4. verify the task can materialize current.json, immutable manifest and dataset and validate hashes;
5. only then assess CISS automation and monitor reactivation.

Until then, scheduled production remains disabled and fail-closed.
