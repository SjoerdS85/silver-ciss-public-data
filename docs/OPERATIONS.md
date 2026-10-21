# Operations

## Modes

1. Audit acquisition: manual workflow only. Fetch the official ECB full and tail payloads and retain them as a GitHub Actions artifact for schema and metadata inspection.
2. Production acquisition: disabled until all public GitHub production gates have passed and Regie separately approves activation.

## Fail-closed rules

- No trusted publication while the schema adapter is unverified.
- No trusted publication on validation, freshness, release-audit or baseline-reconciliation failure.
- No automatic DBnomics fallback.
- No cached stale data promoted as current.
- Current pointer is published last.
- Monitor reactivation is outside this repository and requires separate Regie approval.

## Required evidence before production

- successful official ECB fetch from a GitHub-hosted runner;
- audited ECB payload schema and metadata;
- controlled DB31 baseline export and exact reconciliation;
- current-month and completed-month stress reconstruction where applicable;
- immutable GitHub release configuration verified;
- protected main branch or repository ruleset;
- GitHub Pages read-only publication path;
- hash-based read-back verification;
- failure-injection tests.
