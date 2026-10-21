# Free production architecture

The AWS paid/OIDC production leg is abandoned. The approved free-only direction is: official ECB CISS -> GitHub Actions -> strict validation and DB31 reconciliation -> immutable GitHub Release snapshots plus GitHub Pages current endpoint -> future ChatGPT Scheduled Task.

This is a governance substitution, not an assertion that GitHub is identical to S3 Object Lock/WORM. Before production, Regie requires verified release immutability, protected main/rules, pinned actions, SHA-256 manifests, read-back verification, failure injection and a separate go/no-go.

The exact CISS series, accepted model rules, baseline reconciliation and monitor governance remain unchanged.
