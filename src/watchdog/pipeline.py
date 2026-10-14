
"""Core weekly analysis and evidence-grounded Phase 3 output generation."""

from pathlib import Path

import pandas as pd

from .baselines import add_baselines
from .flags import apply_flags
from .loader import load_shipments
from .weekly import build_weekly_costs
from .retrieval import retrieve_notes, retrieve_notes_semantic
from .explain import explain_row
from .verify import select_supporting_note


def format_pct(value: float) -> str:
    """Format a comparison as a percentage string."""
    return "" if pd.isna(value) else f"{value:+.1f}%"


def run_core(
    shipment_path: str | Path,
    output_path: str | Path,
    history_weeks: int = 8,
    own_history_increase_pct: float = 0.10,
    peer_increase_pct: float = 0.10,
    own_history_z_score: float = 2.0,
    notes_path: str | Path | None = None,
    retrieval_top_k: int = 5,
    retrieval_method: str = "semantic",
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
    llm_provider: str = "none",
    llm_model: str = "qwen2.5:7b",
) -> pd.DataFrame:
    """Run deterministic weekly analysis and generate verified explanations."""

    shipments = load_shipments(shipment_path)
    weekly = build_weekly_costs(shipments)

    compared = add_baselines(
        weekly,
        history_weeks=history_weeks,
    )

    analyzed = apply_flags(
        compared,
        own_history_increase_pct,
        peer_increase_pct,
        own_history_z_score,
    )

    flagged = analyzed.loc[analyzed["flagged_bool"]].copy()
    notes = (
        pd.read_csv(notes_path, dtype=str).fillna("")
        if notes_path
        else None
    )

    records = []

    for _, row in flagged.iterrows():
        route = f"{row['origin']}-{row['destination']}"
        note_id = ""
        note_text = ""
        verdict = "unexplained"

        if notes is not None:
            if retrieval_method == "semantic":
                candidates = retrieve_notes_semantic(
                    notes,
                    route,
                    row["week_of"],
                    material=str(row.get("material", "")),
                    top_k=retrieval_top_k,
                    model_name=embedding_model,
                )
            else:
                candidates = retrieve_notes(
                    notes,
                    route,
                    row["week_of"],
                    material=str(row.get("material", "")),
                    top_k=retrieval_top_k,
                )

            note, verdict = select_supporting_note(
                candidates,
                route,
                row["week_of"],
            )

            if note is not None:
                note_id = note.note_id
                note_text = note.text

        cost = round(float(row["cost_per_tonne_km"]), 2)

        own_pct = format_pct(row["vs_own_history_pct"])
        peer_pct = format_pct(row["vs_similar_routes_pct"])

        records.append(
            {
                "route": route,
                "week_of": row["week_of"].strftime("%Y-%m-%d"),
                "cost_per_tonne_km": cost,
                "vs_own_history": (
                    f"{own_pct} vs this route's past average"
                    if own_pct
                    else ""
                ),
                "vs_similar_routes": (
                    f"{peer_pct} vs similar-length routes this week"
                    if peer_pct
                    else ""
                ),
                "flagged": (
                    "No (justified)"
                    if verdict == "justified"
                    else "Yes"
                ),
                "matched_note_id": note_id,
                "reason": explain_row(
                    {
                        "cost_per_tonne_km": cost,
                        "vs_own_history": own_pct,
                        "vs_similar_routes": peer_pct,
                        "own_history_weeks_used": int(
                            row["own_history_weeks_used"]
                        ),
                    },
                    note_id,
                    note_text,
                    provider=llm_provider,
                    model=llm_model,
                ),
            }
        )

    columns = [
        "route",
        "week_of",
        "cost_per_tonne_km",
        "vs_own_history",
        "vs_similar_routes",
        "flagged",
        "matched_note_id",
        "reason",
    ]

    output = pd.DataFrame(records, columns=columns)

    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(target, index=False)

    return analyzed
