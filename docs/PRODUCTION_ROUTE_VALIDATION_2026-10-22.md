# Production route validation — 2026-10-22

Status: VERIFIED for the external GitHub producer/publication route.

## Verified path

Official ECB CISS
-> GitHub-hosted acquisition
-> schema validation
-> release calendar/freshness audit
-> DB31 reconciliation and accepted revision fingerprint
-> canonical dataset
-> immutable GitHub Release
-> GitHub Pages
-> independent public HTTPS read-back

## First verified immutable publication

Release tag:
ciss-20261020-01a9f9279038

Evidence:
- GitHub Release immutable=true
- canonical rows: 12,217
- first observation: 1980-01-03
- last observation: 2026-10-20
- dataset SHA-256: 01a9f927903828677dbd8349f92c9aebc43922022a3537bfc21ec5f2e529aff1
- manifest SHA-256: 41fcf0adc4f349140059cbf292854d9e632018fe07002a93c97025d06f115cbb
- revision report SHA-256: 08b533af543b5d586bf6830f20d26f9d8620665994e946cfe3add2b8bda91935
- freshness: HEALTHY
- revision governance: ACCEPTED_CURRENT_VINTAGE

## Independent consumer read-back

A separate read-only GitHub-hosted runner fetched:
- Pages current.json
- Pages ciss_current.csv
- Pages ciss_current_manifest.json
- immutable Release ciss_snapshot.csv
- immutable Release ciss_snapshot_manifest.json
- public GitHub Release API metadata

The audit verified:
- Pages dataset equals immutable Release dataset byte-for-byte;
- Pages manifest equals immutable Release manifest byte-for-byte;
- current.json dataset and manifest hashes match downloaded bytes;
- GitHub Release asset digests match the same hashes;
- release immutable=true;
- revision-report digest matches the accepted revision fingerprint;
- current publication TTL was valid;
- series identity and publication state were correct.

Result: PASS.

## Gate conclusion

PRODUCTION_ROUTE_VERIFIED=YES applies to the external producer, archive and public read-only publication route.

It does not yet imply:
- scheduled production enabled;
- ChatGPT Scheduled Task consumer route verified;
- CISS_AUTOMATION unblocked;
- Guardrail or Full Monitor reactivated.

Those require the separate Regie go-live and task-consumer probe.
