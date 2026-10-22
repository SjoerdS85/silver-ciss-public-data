# Publication architecture

## v2 — Connector Snapshot Architecture

The producer remains the verified GitHub-hosted ECB acquisition/validation path. The consumer path adds an immutable Git-tagged snapshot specifically for ChatGPT Scheduled Tasks whose direct DNS/HTTP route is unavailable.

### Producer gates

Every successful candidate must:

1. fetch the exact official ECB full and tail payloads;
2. validate schema and full/tail parity;
3. run release-calendar/freshness audit;
4. enforce five missing expected business days as FAILED;
5. reconcile against the immutable DB31 model vintage;
6. require accepted revision governance;
7. build the canonical full-history CSV;
8. create deterministic manifest and connector attestation.

No scheduled production time is configured until a separate Regie go-live decision.

### Data-only tagged snapshot

A release run creates an orphan Git commit containing only:

```text
connector_snapshot/
  connector_attestation.json
  ciss_snapshot.csv
  ciss_snapshot_manifest.json
  revision_report.csv
```

The release tag is unique per successful retrieval:

```text
ciss-v2-<latest-observation>-<retrieval-utc>-<dataset-sha12>
```

The immutable GitHub Release is targeted at that data-only commit. After publication the workflow verifies:

- `immutable=true`;
- the immutable tag resolves to the data-only commit;
- all four Release asset SHA-256 digests equal the locally built files;
- all four files can be fetched from the GitHub Contents API using `ref=<immutable-tag>`;
- the fetched tagged-tree bytes equal the built bytes.

The temporary staging branch is deleted only after those checks pass; the immutable tag keeps the snapshot commit reachable.

### Connector attestation

`connector_attestation.json` binds:

- exact source/series/frequency/unit;
- publication and TTL timestamps;
- validation, freshness, release-audit and revision-governance states;
- row count and observation coverage;
- Release-asset SHA-256 values;
- tagged-file Git blob SHAs;
- model/calculation versions;
- derived audit metadata.

The attestation does not contain its own digest. Its identity is instead bound by the immutable release tag plus the GitHub connector-reported Git blob SHA; the same attestation is also stored as an immutable Release asset.

### Scheduled Task consumption

The intended v2 Task flow is:

1. latest Release metadata via connected GitHub app;
2. require `immutable=true` and v2 tag;
3. fetch `connector_snapshot/connector_attestation.json` with `ref=<tag>`;
4. fetch manifest and full dataset with the same immutable tag;
5. compare connector-reported Git blob SHAs with the attestation;
6. compare attested SHA-256 values with immutable Release asset digests;
7. verify series/status/TTL/rowcount/coverage;
8. parse the full history;
9. calculate completed monthly means and prior-only expanding P75/P95;
10. calculate the current partial-month asymmetry and exclusive stress phase;
11. fail closed on any mismatch.

The publisher may expose diagnostic model-audit fields, but the Scheduled Task remains responsible for the frozen v0.2 stress calculation before normal monitor use.

### GitHub Pages

Pages remains an independent public read-back surface. It is not the Task transport after the observed Scheduled Task DNS failures.

### Activation

The v2 workflow remains manual-only until the actual Scheduled Task proves full dataset retrieval, integrity checks, full-history parsing, CISS method reproduction and failure behavior.
