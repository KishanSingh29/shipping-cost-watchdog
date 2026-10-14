"""Grounded explanation generation with optional local Ollama and safe fallback."""
from __future__ import annotations
import hashlib, json, time
from pathlib import Path
from typing import Any
import pandas as pd


def _template(row: dict[str, Any], note_id: str = "", note_text: str = "") -> str:
    own = row.get("vs_own_history", "")
    peer = row.get("vs_similar_routes", "")
    if not note_id:
        return (f"Cost per tonne-km is {own} above its prior-history average and {peer} above same-week peers; "
                "no matching note passed route, date, and cost-impact checks. The rise is unexplained.")
    return f"Note {note_id} states: {note_text} This note passed route, date-window, and cost-increase checks; it is evidence of a possible cause, not proof that it explains the full increase."


def explain_row(row: dict[str, Any], note_id: str = "", note_text: str = "", *,
                cache_dir: str = "outputs/llm_cache", token_log: str = "outputs/token_log.csv",
                provider: str = "none", model: str = "qwen2.5:7b", ollama_url: str = "http://localhost:11434") -> str:
    """Use local Ollama only for wording; fall back safely if unavailable or invalid."""
    fallback = _template(row, note_id, note_text)
    if not note_id or provider.lower() != "ollama":
        return fallback
    prompt = ("Write 1-2 plain-English sentences using ONLY this JSON evidence. Do not add facts. "
              "Mention the note ID. Do not alter the verdict. Evidence: " + json.dumps({"row": row, "verdict": "justified", "note_id": note_id, "note_text": note_text}, sort_keys=True))
    key = hashlib.sha256(prompt.encode()).hexdigest()
    cache = Path(cache_dir); cache.mkdir(parents=True, exist_ok=True)
    cache_file = cache / f"{key}.json"
    if cache_file.exists():
        try:
            return json.loads(cache_file.read_text(encoding="utf-8"))["text"]
        except (ValueError, KeyError):
            pass
    start = time.perf_counter(); input_tokens = output_tokens = 0; calls = 1
    try:
        import requests
        response = requests.post(f"{ollama_url.rstrip('/')}/api/generate", json={"model": model, "prompt": prompt, "stream": False, "options": {"temperature": 0, "seed": 0}}, timeout=90)
        response.raise_for_status(); data = response.json(); text = str(data.get("response", "")).strip()
        # Ollama reports token counts, unlike generic string estimates.
        input_tokens = int(data.get("prompt_eval_count", 0)); output_tokens = int(data.get("eval_count", 0))
        # Conservative grounding post-check: cited ID must appear and output must not be empty.
        if not text or note_id not in text:
            text = fallback
        else:
            # Require a date or distinctive content phrase from the source to reduce unsupported claims.
            words = [w.lower() for w in note_text.split() if len(w) >= 5]
            if not any(w in text.lower() for w in words[:8]):
                text = fallback
        if text != fallback:
            cache_file.write_text(json.dumps({"text": text}, ensure_ascii=False), encoding="utf-8")
    except Exception:
        text = fallback
    latency_ms = round((time.perf_counter() - start) * 1000, 2)
    Path(token_log).parent.mkdir(parents=True, exist_ok=True)
    log_path = Path(token_log)
    record = pd.DataFrame([{"prompt_hash": key, "model": model, "input_tokens": input_tokens,
                            "output_tokens": output_tokens, "calls": calls, "latency_ms": latency_ms,
                            "estimated_cost_usd": 0.0, "used_fallback": text == fallback}])
    record.to_csv(log_path, mode="a", header=not log_path.exists(), index=False)
    return text
