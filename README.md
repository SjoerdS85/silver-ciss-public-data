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
- GitHub release immutability: required before first publication and not yet operationally verified.
- GitHub Pages: required before first publication and not yet operationally verified.
- Scheduled production: disabled.
- Silver monitor reactivation: outside this repository and requires separate Regie approval.

## Free production architecture

Official ECB CISS
-> GitHub Actions
-> schema + freshness + DB31/revision governance
-> content-addressed immutable GitHub Release
+ GitHub Pages current read-only surface
-> future ChatGPT Scheduled Task

No AWS credentials, long-lived cloud credentials, private project data or secrets belong in this repository.

## Repository layout

- config/ — frozen source, revision and release contracts
- src/ — acquisition, validation, reconciliation, stress and publication helpers
- tests/ — deterministic contract, failure and publication tests
- baseline/ — controlled accepted DB31 model vintage
- docs/ — architecture, operations and security notes
- .github/workflows/ — CI and gated audit/publication workflows
- public/ — reserved publication documentation

## Remaining production gates

Before scheduled publication is enabled, Regie still requires:
1. immutable releases enabled and verified on a real future release;
2. GitHub Pages configured for GitHub Actions;
3. one manual end-to-end publication run;
4. external read-back of Pages and immutable Release assets;
5. independent hash verification;
6. separate production go/no-go;
7. only then a scheduled production trigger and future task probe.

Until those gates pass, scheduled production remains disabled and fail-closed.
