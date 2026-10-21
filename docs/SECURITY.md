# Security model

- Public repository contains only non-sensitive code, public CISS data and public integrity metadata.
- No AWS credentials, access keys, private keys or project secrets are permitted.
- GitHub Actions permissions remain least-privilege.
- Workflow dependencies are pinned by full commit SHA.
- Main branch protection or an equivalent ruleset is a production gate.
- GitHub release immutability must be enabled and verified before production.
- Public current data is served read-only through GitHub Pages.
- Publication manifests carry SHA-256 integrity hashes.
- Production remains fail-closed until separate Regie approval.
