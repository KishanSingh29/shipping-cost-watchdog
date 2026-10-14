# Shipping Cost Watchdog

A reproducible Python 3.11+ case-study project that detects unusual weekly freight costs, compares them with route history and peer routes, and conservatively checks context notes before citing a reason.

> Current delivery is the complete deterministic baseline and project packaging. The default retrieval method is TF-IDF so the project runs without downloading a neural model. A Sentence Transformers semantic-retrieval adapter exists in `src/watchdog/retrieval.py`, but the full semantic RAG path should be enabled and verified in a later implementation step. Do not claim real embedding inference has been validated by the current test suite.

## Quick start

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

Windows PowerShell:

```powershell
$env:PYTHONPATH = "src"
pytest -q
python -m watchdog.cli
python eval/run_eval.py
python scripts/audit_output.py
```

macOS/Linux:

```bash
export PYTHONPATH=src
pytest -q
python -m watchdog.cli
python eval/run_eval.py
python scripts/audit_output.py
```

To test repeatability on macOS/Linux: `bash scripts/repro_check.sh`. It writes three output copies and a SHA-256 report.

## Architecture

```text
shipment_records.csv
  -> schema and value validation
  -> week starts (Monday)
  -> route-week weighted cost/tonne-km
  -> strictly prior rolling history and same-week peer baseline
  -> deterministic anomaly flags
  -> retrieve context notes (TF-IDF baseline by default)
  -> independent rule gate: route + time + positive cost effect + plausible cause
  -> note ID or unexplained
  -> deterministic explanation template (optional local Ollama for wording only)
  -> output CSV + citation audit + logs
```

## Key decisions and assumptions

- Route identity is the directed `(origin, destination)` pair, with `route_type` included in the weekly group.
- Weekly cost/tonne-km is `sum(freight_cost_inr) / sum(quantity_tonnes * distance_km)` per route-week.
- Weeks run Monday through Sunday; `week_of` is Monday.
- History uses only the previous up-to-eight observed route-weeks. No prior weeks means no history baseline and the row cannot be flagged.
- Peer baseline is the same week and `route_type`, excluding the current route.
- Flag thresholds in `config.yaml` are explicit starting assumptions, not trained values. Review/tune only with documented reasoning; don't tune against held-out labels.
- Invalid rows raise an error with shipment IDs. The loader does not silently drop them.
- The supplied output-format CSV has malformed example rows with unquoted commas in prose. The output header follows the eight named columns in the template, and output values are written by pandas with correct CSV quoting.
- A matching note is not enough by itself. Rule-based checks reject wrong route, wrong time, negative/no-change wording, and implausible causes. An unexplained result is preferred over an unsupported citation.
- Current template has 30 proposed evaluation cases but deliberately blank expected verdict/note labels. The developer/user must manually label them from the source notes before metrics are meaningful. No ground truth is invented.
- The citation auditor is a separate conservative cross-check, not a formal proof. Complex effective-date phrasing should still receive human review.

## Config

`config.yaml` contains input/output paths, thresholds, history window, retrieval method/model, and optional LLM settings. Default `retrieval.method` is `tfidf` to keep the baseline runnable without model downloads. `semantic` uses the Sentence Transformers adapter and requires downloading the model. `llm.provider: none` means no LLM calls; optional `ollama` only changes wording and must not alter flags/citations.

## Evaluation and trust

- Unit tests: run `pytest -q`.
- Human-labeled evaluation template: `eval/labeled_cases.csv`.
- Evaluation script: `python eval/run_eval.py`. It explicitly reports no metrics until the expected labels are filled.
- Independent citation auditor: `python scripts/audit_output.py`.
- Reproducibility script: `bash scripts/repro_check.sh` on macOS/Linux.
- Token log: `outputs/token_log.csv` is generated only if an Ollama call is made. No live LLM call means no token usage is claimed.
- Current local build tests use deterministic fixtures; the real sentence-transformers model and Ollama are not considered validated until run on the user's machine.

## Known limitations

- The default TF-IDF retriever is lexical, not full semantic RAG.
- Date-window verification uses conservative text rules and needs manually labeled adversarial testing.
- The LLM grounding post-check is a guardrail, not a proof that every sentence is entailed. Use deterministic templates if strict auditability is required.
- Evaluation metrics remain unavailable until the 30 proposed cases are manually labeled.
- Cost estimate is zero when no external paid API is used; local inference still has hardware/electricity cost not represented as API spend.

## Ten-minute walkthrough

1. Show the source columns and data findings.
2. Explain the weighted weekly cost formula.
3. Explain why historical windows exclude the current week.
4. Show peer comparison excluding the current route.
5. Walk through one flagged route-week.
6. Show why retrieval similarity cannot directly justify a note.
7. Demonstrate negative-note and wrong-route rejection tests.
8. Run unit tests, citation auditor, and reproducibility check.
9. Explain current TF-IDF baseline vs planned semantic RAG upgrade honestly.
10. Show the blank evaluation labels and explain that you will label them yourself rather than invent ground truth.
