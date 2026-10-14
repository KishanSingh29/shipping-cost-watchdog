# Phase 3 — Retrieval and verification gate

## What is implemented

- Deterministic local TF-IDF retrieval over `applies_to` + note text. Similarity ranks candidates only; it cannot approve a citation.
- Optional local semantic retrieval adapter using `sentence-transformers/all-MiniLM-L6-v2` is available as `retrieve_notes_semantic`. It is opt-in because the model must be downloaded and installed; the default run does not need a network or model download.
- Rule-based verification checks route scope, effective date window, positive cost-increase direction, and plausible cause type.
- Explicit recovery language overrides the preceding-week grace period. This prevents the flooding note from justifying the week beginning 2025-03-10 after the note says roads were passable again by Mar 9.
- Verified note selection is deterministic: highest retrieval score, then `note_id` as tie-breaker.
- Unverified rows have blank `matched_note_id` and remain flagged for review.
- Explanations are deterministic templates and include the exact note text for verified matches. No LLM is used in this phase.

## Actual results on supplied inputs

| Route | Week | Verdict (`flagged` field) | Matched note |
|---|---|---|---|
| Delhi-Jaipur | 2024-11-11 | Yes — unexplained | blank |
| Ahmedabad-Mumbai | 2025-01-20 | No (justified) | N002 |
| Chennai-Bangalore | 2025-02-24 | No (justified) | N001 |
| Chennai-Bangalore | 2025-03-10 | Yes — unexplained | blank |
| Mumbai-Delhi | 2025-05-12 | No (justified) | N003 |

`flagged` uses the supplied output contract's convention: `Yes` means flag for human review; `No (justified)` means a note passed the verification gate. A matching note is not proof that it explains the entire size of the anomaly; the reason explicitly calls for reviewing the magnitude.

## Tests

`PYTHONPATH=src pytest -q` → 13 passed.

Coverage includes positive flood evidence, post-recovery rejection, wrong-route rejection, negative evidence rejection, all-routes fuel note, no-support fallback, deterministic ranking, and the Phase 2 numerical tests.

## Known limitation / trade-off

The default pipeline uses TF-IDF rather than embedding inference, to keep the assessment runnable without a large model download. An optional sentence-transformers adapter is included for a local semantic retrieval run. Before claiming embedding-based RAG in a demo, install the optional dependency, run that path, and compare retrieval results. Verification remains mandatory either way.
