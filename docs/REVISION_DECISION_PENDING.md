# Pending CISS revision-governance decision

The accepted DB31 baseline remains the immutable model vintage used for the 2026-09-12 validation cut.

The current official ECB vintage differs from that baseline on 1,018 dates after explicit four-decimal comparison normalization. There are no missing or extra dates through the cut. The largest four-decimal difference is 0.0014, and the full model-impact audit found zero NORMAL/ELEVATED/EXTREME classification changes across 559 completed common months.

The September 2026 prior-only thresholds move only slightly:

- accepted DB31 P75: 0.1745166666666666666666666667
- current official P75: 0.1745294460268478755952380952
- accepted DB31 P95: 0.4310364285714285714285714286
- current official P95: 0.4310231641276560236666666667

September remains NORMAL; October partial remains NORMAL with stress vote 0.

## Proposed disposition

The technically preferred governance treatment is:

**accept the current official ECB vintage for ongoing operational CISS calculations while preserving DB31 unchanged as the accepted historical model vintage.**

This avoids freezing the operational monitor to a stale historical extract while maintaining full reproducibility of the accepted September 2026 research state.

The repository deliberately leaves this decision at `PENDING_REGIE_DISPOSITION`. Trusted publication remains blocked until Regie explicitly accepts or rejects this treatment.
