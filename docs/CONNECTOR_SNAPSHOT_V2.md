# Connector Snapshot v2 — governance record

Approved by Regie on 2026-10-22 after:

- direct Scheduled Task DNS failure for `sjoerds85.github.io`;
- direct Scheduled Task DNS failure for `github.com`, `api.github.com` and `raw.githubusercontent.com`;
- successful Scheduled Task use of the connected GitHub app for immutable Release metadata and repository text-file retrieval.

## Scope

This changes only the CISS transport/consumption layer. It does not change:

- CISS series identity;
- DB31 historical model vintage;
- prior-only expanding quantile method;
- stress thresholds or phase rules;
- Silver Signal Model v0.2;
- monitor evidence families;
- scenario ranges;
- trading interpretation.

## Integrity model

The immutable Release contributes SHA-256 asset digests and an immutable tag.

The immutable tag points to a data-only Git commit containing the full dataset, manifest, revision report and connector attestation. The GitHub connector returns each file's Git blob SHA and content for a requested tag reference.

The Task must require both chains:

```text
immutable Release metadata
  -> immutable tag
  -> Release asset SHA-256 digests

immutable tag
  -> tagged connector_attestation.json
  -> expected Git blob SHAs
  -> tagged manifest/full dataset/revision report
```

The Task must also materialize and parse the full dataset and reproduce the frozen CISS method. Metadata-only success is insufficient.

## Current gate

Until a real v2 snapshot and Task probe pass:

```text
GITHUB_CONNECTOR_TASK_ROUTE=PASS_METADATA_ONLY
CONNECTOR_SNAPSHOT_V2=PENDING_REAL_PUBLICATION
AUTOMATIC_CISS_ROUTE_VERIFIED=NO
SCHEDULED_PRODUCTION=DISABLED
SILVER_GUARDRAIL_WATCH=PAUSED
SILVER_FULL_MONITOR=PAUSED
```
