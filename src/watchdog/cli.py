"""Command-line entry point for Phase 2 core logic."""
import argparse
from pathlib import Path
from .config import load_config
from .pipeline import run_core


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Shipping Cost Watchdog core analysis")
    parser.add_argument("--config", default="config.yaml", help="Path to YAML config")
    args = parser.parse_args()
    config = load_config(args.config)
    paths = config["paths"]
    thresholds = config["thresholds"]
    history = config["history"]
    analyzed = run_core(
        paths["shipments"], paths["output"], history_weeks=int(history["weeks"]),
        notes_path=paths.get("notes"), retrieval_top_k=int(config.get("retrieval", {}).get("top_k", 5)),
        own_history_increase_pct=float(thresholds["own_history_increase_pct"]),
        peer_increase_pct=float(thresholds["peer_increase_pct"]),
        own_history_z_score=float(thresholds["own_history_z_score"]),
        retrieval_method=str(config.get("retrieval", {}).get("method", "semantic")),
        embedding_model=str(config.get("retrieval", {}).get("model", "sentence-transformers/all-MiniLM-L6-v2")),
        llm_provider=str(config.get("llm", {}).get("provider", "none")),
        llm_model=str(config.get("llm", {}).get("model", "qwen2.5:7b")),
    )
    flagged = int(analyzed["flagged_bool"].sum())
    print(f"Weekly route rows analyzed: {len(analyzed)}")
    print(f"Flags written: {flagged}")
    print(f"Output: {Path(paths['output'])}")


if __name__ == "__main__":
    main()
