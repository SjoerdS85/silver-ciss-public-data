# silver-ciss-public-data

Public reproducible CISS acquisition and publication layer for Silver Market Research.

## Purpose

This repository is the free/public production route for the exact ECB CISS series:

`CISS.D.U2.Z0Z.4F.EC.SS_CIN.IDX`

Primary source: official ECB Data API.

It replaces only the external AWS/S3 publication layer that was previously proposed. The accepted signal-model definitions, CISS calculation rules, source identity, baseline reconciliation requirements and Regie approval gates remain unchanged.

## Current status

- Public GitHub repository: active.
- Official ECB source contract: frozen.
- Schema adapter: not yet verified against a successful external GitHub-hosted fetch.
- DB31 baseline reconciliation: still required before production.
- GitHub release immutability: required and not yet verified.
- GitHub Pages read-only publication: required and not yet enabled.
- Production publication: disabled/fail-closed.
- Silver monitor reactivation: outside this repository and requires separate Regie approval.

## Free production architecture

```text
Official ECB CISS
      |
GitHub Actions (public repository)
      |
strict validation + DB31 reconciliation
      |
GitHub Release snapshot archive
      +
GitHub Pages current read-only surface
      |
future ChatGPT Scheduled Task
```

No AWS credentials, long-lived cloud credentials, private project data or secrets belong in this repository.

## Repository layout

- `config/` — frozen source/model/publication contract
- `src/` — acquisition, validation, reconciliation and stress calculation helpers
- `tests/` — deterministic contract and model tests
- `baseline/` — controlled baseline onboarding instructions
- `docs/` — architecture, operations and security notes
- `.github/workflows/` — CI and manual external-route audit workflow
- `public/` — future GitHub Pages publication root

## Production gates

A successful CI run is not production approval. Before publication is enabled, Regie requires at minimum:

1. successful official ECB fetch from a GitHub-hosted runner;
2. audited real ECB CSV schema/metadata and verified schema adapter;
3. controlled DB31 baseline export and exact full-history reconciliation;
4. September 2026 completed/current reconstruction as applicable;
5. verified GitHub release immutability configuration;
6. branch/rules protection and least-privilege workflow permissions;
7. GitHub Pages read-only endpoint and hash-based read-back;
8. failure-injection tests;
9. separate Regie go/no-go.

Until all gates pass, the route remains fail-closed.
