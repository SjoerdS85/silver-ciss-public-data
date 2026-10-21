# Accepted DB31 baseline

Production onboarding uses a controlled export from the accepted DB31 workbook.

Required workbook SHA-256:
`e5efd6d729cca0d2d79f49b9a2262db3517a595f9eeae68ddda58a85579fa151`

Controlled export contract:
- file: `baseline/ciss_db31_accepted_20260910.csv`
- CSV SHA-256: `40e1d3d78b743b8f4e69b3a50d1f620b2e3c35156481b69fe346e571369c4d34`
- 12,189 observations
- first date 1980-01-03
- last date 2026-09-10
- exact series `CISS.D.U2.Z0Z.4F.EC.SS_CIN.IDX`
- values serialized with exactly four decimal places
- LF line endings

The CSV is an export of the accepted model vintage. It is not the original ECB HTTP response body and must never be represented as such.

The manifest in this directory is authoritative for the controlled-export hash and provenance. Production reconciliation must refuse a baseline file whose SHA-256 does not match the manifest.
