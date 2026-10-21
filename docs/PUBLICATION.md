# Publication architecture

The production publication path is content-addressed and fail-closed.

## Build

A publication build:
1. fetches the exact official ECB full and tail payloads;
2. validates schema and full/tail parity;
3. runs the verified release-calendar and freshness audit;
4. reconciles against the immutable DB31 model vintage;
5. requires the exact accepted revision fingerprint, or no historical revisions;
6. writes a canonical full-history CSV;
7. hashes the dataset and manifest;
8. derives a content-addressed release tag;
9. builds the GitHub Pages current surface.

## Immutable archive

The future production workflow creates three GitHub Release assets:
- ciss_snapshot.csv
- ciss_snapshot_manifest.json
- revision_report.csv

Production requires repository-level immutable releases to be enabled before the first production release. After creating a release, the workflow queries the release object and requires immutable=true; otherwise the run fails.

The release tag is derived from the latest official observation plus the first 12 hex characters of the canonical dataset SHA-256.

## Read-only current surface

GitHub Pages publishes:
- /ciss/v1/current.json
- /ciss/v1/ciss_current.csv
- /ciss/v1/ciss_current_manifest.json

current.json points to the immutable Release assets and includes both dataset and manifest SHA-256 values. The Pages copies exist for simple read-only access; the immutable Release remains the archival snapshot.

## Production activation

The workflow is intentionally manual-only at this stage. A scheduled trigger is added only after immutable releases, Pages deployment, external read-back, hash verification, and Regie go/no-go have all passed.
