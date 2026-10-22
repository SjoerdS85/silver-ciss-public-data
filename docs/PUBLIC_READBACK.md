# Public HTTPS read-back audit

This audit runs on a separate GitHub-hosted runner after the first publication route exists.

It reads the public GitHub Pages current pointer, downloads the immutable GitHub Release dataset and manifest through their public HTTPS URLs, reads the Pages copies, and independently verifies:

- current pointer status and TTL;
- immutable Release flag;
- dataset SHA-256;
- manifest SHA-256;
- revision-report asset digest;
- exact equality of Pages dataset versus Release dataset;
- exact equality of Pages manifest versus Release manifest;
- series identity and publication status.

The workflow uses no repository write permission and no private data. Its purpose is to verify the public consumer route, not merely the producer's local files.
