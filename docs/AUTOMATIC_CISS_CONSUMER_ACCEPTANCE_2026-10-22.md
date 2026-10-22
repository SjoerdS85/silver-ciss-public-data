# CISS automatic consumer acceptance — 2026-10-22

Status: PASS

The real ChatGPT Scheduled Task runtime completed an end-to-end CISS consumer probe at approximately 10:14 Europe/Amsterdam on 2026-10-22 using only the connected GitHub app.

The probe materialized the full canonical dataset (323,763 bytes; 12,217 unique observations), verified immutable Release metadata and all required SHA-256/Git blob identities, checked TTL/freshness, parsed the full history and independently reproduced the accepted CISS monthly/quantile/stress calculations within tolerance 1e-12.

Accepted immutable v2 release:
`ciss-v2-20261020-20261022T080329Z-01a9f9279038`

Canonical conclusion:

```text
AUTOMATIC_CISS_ROUTE_VERIFIED=YES
PRODUCER_ROUTE_VERIFIED=YES
DIRECT_TASK_HTTPS=FAIL
GITHUB_CONNECTOR_TASK_ROUTE=PASS
SCHEDULED_PRODUCTION=DISABLED
SILVER_GUARDRAIL_WATCH=PAUSED
SILVER_FULL_MONITOR=PAUSED
RECALIBRATION_REQUIRED=YES
```

The direct-HTTPS DNS failures are retained as factual incident history; they are no longer blocking because the approved connector transport is independently verified end to end.
