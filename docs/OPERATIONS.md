# Operations

## Modes

1. Audit acquisition: manual workflow only. Fetch the official ECB full and tail payloads and retain them as a GitHub Actions artifact for schema and metadata inspection.
2. Production acquisition: disabled until all public GitHub production gates have passed and Regie separately approves activation.

## Current audited state

The first GitHub-hosted official ECB acquisition succeeded on 2026-10-21. The exact series and CSV schema are now verified, including raw OBS_VALUE precision beyond the DECIMALS=4 metadata attribute.

The accepted DB31 baseline has not yet passed current-vintage reconciliation. The first diagnostic comparison found official historical revisions, so production remains blocked under `HOLD_REVISION`.

## Fail-closed rules

- No trusted publication while schema, freshness, release audit or baseline revision governance is unresolved.
- No automatic DBnomics fallback.
- No cached stale data promoted as current.
- Current pointer is published last.
- Raw official decimals are preserved exactly; four-decimal normalization is used only for comparison with the accepted DB31 four-decimal vintage.
- Monitor reactivation is outside this repository and requires separate Regie approval.

## Required evidence before production

- controlled DB31 baseline CSV available to the pipeline with verified hash;
- full revision report and formal Regie disposition of current-vintage revisions;
- current-month and completed-month stress reconstruction;
- release-calendar and freshness validation;
- immutable GitHub release configuration verified;
- protected main branch or repository ruleset;
- GitHub Pages read-only publication path;
- hash-based read-back verification;
- failure-injection tests.
