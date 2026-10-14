"""Evaluate predictions against human labels. Blank labels are intentionally not scored."""
from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd

REQUIRED = {"case_id", "expected_flagged", "expected_verdict", "expected_note_id"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--labels", default="eval/labeled_cases.csv")
    parser.add_argument("--predictions", default="outputs/watchlist.csv")
    parser.add_argument("--out", default="outputs/eval_report.md")
    args = parser.parse_args()
    labels = pd.read_csv(args.labels, dtype=str).fillna("")
    missing = REQUIRED - set(labels.columns)
    if missing:
        raise SystemExit(f"Label file missing columns: {sorted(missing)}")
    pred_path = Path(args.predictions)
    if not pred_path.exists():
        raise SystemExit(f"Predictions not found: {pred_path}")
    predictions = pd.read_csv(pred_path, dtype=str).fillna("")
    labelled = labels[labels["expected_flagged"].isin(["0", "1"]) & labels["expected_verdict"].ne("")].copy()
    report = ["# Evaluation report", "", f"Cases in template: {len(labels)}", f"Cases manually labelled: {len(labelled)}", ""]
    if labelled.empty:
        report += ["No metrics computed: expected labels are blank by design. A human must inspect raw notes and fill expected_flagged, expected_verdict, and expected_note_id before scoring.", "", "This is intentional; the tool does not fabricate ground-truth labels."]
    else:
        merged = labelled.merge(predictions, left_on=["route", "week_of"], right_on=["route", "week_of"], how="left", suffixes=("_expected", "_actual"))
        actual_flag = merged.get("flagged", pd.Series("", index=merged.index)).eq("Yes")
        expected_flag = merged["expected_flagged"].eq("1")
        verdict_actual = merged.get("flagged", pd.Series("", index=merged.index)).map(lambda x: "justified" if x == "No (justified)" else "unexplained" if x == "Yes" else "not_flagged")
        expected_verdict = merged["expected_verdict"]
        note_actual = merged.get("matched_note_id", pd.Series("", index=merged.index))
        report += [f"Flag accuracy: {(actual_flag == expected_flag).mean():.3f}", f"Verdict accuracy (labelled rows): {(verdict_actual == expected_verdict).mean():.3f}", f"Note ID accuracy: {(note_actual == merged['expected_note_id']).mean():.3f}", "", "## Labelled case results", "", merged[["case_id", "route", "week_of", "expected_flagged", "expected_verdict", "expected_note_id"]].to_markdown(index=False)]
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text("\n".join(report) + "\n", encoding="utf-8")
    print("\n".join(report))

if __name__ == "__main__":
    main()
