# Phase 2 core-only repeatability check

Three fresh executions of the deterministic Phase 2 core pipeline produced byte-identical `watchlist.csv` files.

- Run 1 SHA-256: `439d52b0c8e861e3488888d60b2a84cfffc6805ff955387cf66afbe20b77af18`
- Run 2 SHA-256: `439d52b0c8e861e3488888d60b2a84cfffc6805ff955387cf66afbe20b77af18`
- Run 3 SHA-256: `439d52b0c8e861e3488888d60b2a84cfffc6805ff955387cf66afbe20b77af18`

Pairwise diffs were empty. This is a core-only check, not yet the full Phase 6 pipeline check; retrieval, explanation, token logs, and final verdicts are not implemented yet.
