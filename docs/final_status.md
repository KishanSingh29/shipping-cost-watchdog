# Final build status (current local environment)

- Core test suite: 16 passed.
- Weekly route records analysed: 728 (7 directed routes x 104 weeks).
- Flagged route-week candidates in current configuration: 5.
- Three default runs: byte-identical output CSVs; see `repro_report.md` and `outputs/repro/sha256.txt`.
- Citation auditor: 3 cited rows checked, 0 failures in the current output. This is a lightweight independent check, not a proof of semantic correctness.
- Evaluation template: 30 proposed cases, 0 manually labelled. Metrics are intentionally not reported until labels are completed.
- Default retrieval: TF-IDF. Sentence Transformers adapter is present but real model inference has not been validated in this build environment.
- Default LLM: disabled. No LLM calls or token usage are claimed.
