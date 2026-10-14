"""Independent conservative audit of citations in the final output CSV."""
from __future__ import annotations
import argparse, re
from pathlib import Path
import pandas as pd


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--output", default="outputs/watchlist.csv")
    p.add_argument("--notes", default="data/context_notes.csv")
    p.add_argument("--report", default="outputs/citation_audit.csv")
    args = p.parse_args()
    out = pd.read_csv(args.output, dtype=str).fillna("")
    notes = pd.read_csv(args.notes, dtype=str).fillna("")
    results = []
    for row in out.itertuples(index=False):
        note_id = row.matched_note_id
        if not note_id:
            if row.flagged == "No (justified)":
                results.append({"route": row.route, "week_of": row.week_of, "note_id": "", "audit": "FAIL", "detail": "Justified row has blank note ID"})
            continue
        match = notes[notes.note_id == note_id]
        detail = ""
        ok = len(match) == 1
        if ok:
            note = match.iloc[0]
            applies = str(note.applies_to).strip().lower()
            route_ok = applies == "all routes" or applies == str(row.route).lower()
            text = str(note.note).lower()
            week = pd.Timestamp(row.week_of)
            note_date = pd.Timestamp(note.date)
            # Deliberately conservative independent checks: exact route/all-routes, note date no later than week end,
            # and reject explicit negative/no-change language. Complex date ranges are flagged for manual review.
            date_ok = note_date <= week + pd.Timedelta(days=6) and note_date >= week - pd.Timedelta(days=7)
            negative = any(s in text for s in ["costs were not", "not significantly affected", "without a rate change", "no rate change", "no major disruptions", "no significant disruptions", "improved road conditions"])
            positive = any(s in text for s in ["higher trip costs", "higher costs", "pushing up transportation costs", "surcharge", "rate increase", "increased cost"])
            direction_ok = positive and not negative
            ok = route_ok and date_ok and direction_ok
            detail = f"route_ok={route_ok}; date_ok={date_ok}; positive_cost_impact={direction_ok}"
            if "passable again by" in text or "returned to normal" in text:
                recovery = re.search(r"(?:passable again by|returned to normal)[^.]*?([a-z]{3,9})\s+(\d{1,2})", text)
                if recovery:
                    detail += "; recovery wording requires manual boundary review"
        results.append({"route": row.route, "week_of": row.week_of, "note_id": note_id, "audit": "PASS" if ok else "FAIL", "detail": detail})
    report = pd.DataFrame(results, columns=["route", "week_of", "note_id", "audit", "detail"])
    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    report.to_csv(args.report, index=False)
    failures = int((report.audit == "FAIL").sum()) if not report.empty else 0
    print(f"Citation audit rows: {len(report)}; failures: {failures}; report: {args.report}")
    if failures:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
