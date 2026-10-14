# Phase 4 — Semantic RAG and explanations

## What changed
- The configured default retrieval method is now local semantic embeddings with `sentence-transformers/all-MiniLM-L6-v2`.
- Retrieval ranks notes by cosine similarity on normalized embeddings; ties are broken by `note_id`.
- The existing deterministic verification gate remains authoritative: exact route scope, conservative effective-date overlap, explicit cost-increase direction, and plausible cause must all pass. Similarity alone never creates a citation.
- Explanation generation uses a fixed template by default. Optionally, local Ollama can write wording (`llm.provider: ollama`), but only after the semantic/core verdict and matched note have already been selected.
- Ollama output is cached by prompt SHA-256; calls log token counts reported by Ollama, latency, and $0 local estimated cost. Invalid/unavailable LLM responses fall back to a deterministic template.

## Run
Install dependencies from `requirements.txt` (the sentence-transformers install downloads a local model on first use), then:

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python -m watchdog.cli
```

For optional LLM wording, install and start Ollama, pull the configured model, then set `llm.provider: ollama` in `config.yaml`. No API key is needed for local Ollama.

## Validation in this build environment
- `PYTHONPATH=src pytest -q`: **16 passed**.
- Semantic ranking was unit-tested with a deterministic fake embedding model. The real SentenceTransformer model was **not downloaded/executed in this environment**, because `sentence-transformers` was not installed here. Run the command above to perform the real model inference locally.
- Ollama was not installed/running here, so live LLM calls and provider token counts have not been claimed. The default config uses `llm.provider: none`, so output stays deterministic and no LLM tokens are consumed.

## Trust and limitations
- Semantic retrieval is a candidate-generation step, not a proof of causality.
- Note applicability and time-window parsing are rule-based and deliberately conservative; inspect `verify.py` and manually label edge cases before submission.
- The lightweight explanation post-check checks note ID and a source phrase, not full natural-language entailment. For the highest trust, keep the deterministic template or manually review generated wording.
- Token log records only actual Ollama calls; default template-only runs have no LLM calls to log.
