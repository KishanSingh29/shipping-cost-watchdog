"""Rule-based evidence verification; retrieval similarity never grants support."""
from __future__ import annotations

from dataclasses import dataclass
import re
import pandas as pd
from .retrieval import RetrievedNote


@dataclass(frozen=True)
class VerificationResult:
    """Verification outcome for a route-week candidate note."""
    supported: bool
    reason: str


def _norm(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def _date_window(note: RetrievedNote) -> tuple[pd.Timestamp, pd.Timestamp]:
    """Infer a conservative effective window from explicit note wording.

    A note date is its effective/start date. Explicit ranges such as 'Feb 24 to
    Mar 8' are parsed. Open-ended nationwide changes remain effective onward.
    """
    text = note.text.lower()
    start = pd.Timestamp(note.date).normalize()
    end = start
    # Explicit same-year date ranges, e.g. "from Feb 24 to Mar 8".
    match = re.search(r"(?:from\s+)?([a-z]{3,9})\s+(\d{1,2})\s+to\s+([a-z]{3,9})\s+(\d{1,2})", text)
    if match:
        year = start.year
        try:
            start = pd.Timestamp(f"{match.group(1)} {match.group(2)} {year}")
            end = pd.Timestamp(f"{match.group(3)} {match.group(4)} {year}")
            if end < start:
                end = end + pd.DateOffset(years=1)
            return start.normalize(), end.normalize()
        except (ValueError, TypeError):
            pass
    if any(phrase in text for phrase in ["starting this week", "from this week", "nationwide starting"]):
        return start, pd.Timestamp.max.normalize()
    if "this quarter" in text or "this month" in text:
        return start, start + pd.Timedelta(days=90 if "this quarter" in text else 30)
    if "week" in text or "about a week" in text or "temporary" in text:
        return start, start + pd.Timedelta(days=6)
    return start, start


def _direction_is_increase(text: str) -> bool:
    """Require explicit positive cost/rate language and reject negated claims."""
    t = text.lower()
    negative = ["costs were not", "not significantly affected", "no rate change",
                "no major disruptions", "no significant disruptions", "remained stable",
                "costs weren't", "without a rate change", "improved road conditions",
                "returned to normal", "costs were not affected", "did not affect"]
    if any(term in t for term in negative):
        return False
    positive = ["higher trip costs", "higher costs", "costs", "cost up", "cost increase",
                "pushing up transportation costs", "surcharge", "rate increase", "increased cost"]
    return any(term in t for term in positive)


def _plausible_cause(text: str) -> bool:
    t = text.lower()
    return any(term in t for term in ["fuel", "diesel", "toll", "flood", "weather",
                                      "rain", "storm", "festival", "surcharge", "detour",
                                      "transportation costs"])


def verify_note(note: RetrievedNote, route: str, week_of: str | pd.Timestamp) -> VerificationResult:
    """Validate route scope, effective date, direction, and cause type."""
    route_norm = _norm(route)
    applies_norm = _norm(note.applies_to)
    if applies_norm != "all routes" and applies_norm != route_norm:
        return VerificationResult(False, "route_scope_mismatch")
    week_start = pd.Timestamp(week_of).normalize()
    week_end = week_start + pd.Timedelta(days=6)
    # Explicit recovery statements override the generic preceding-week grace period.
    recovery = re.search(r"(?:passable|returned to normal|repairs were completed)\s+(?:again\s+)?by\s+([a-z]{3,9})\s+(\d{1,2})", note.text.lower())
    if recovery:
        try:
            recovery_date = pd.Timestamp(f"{recovery.group(1)} {recovery.group(2)} {pd.Timestamp(note.date).year}")
            if week_start > recovery_date.normalize():
                return VerificationResult(False, "after_explicit_recovery")
        except ValueError:
            pass
    start, end = _date_window(note)
    # Accept overlap with the flagged week or the immediately preceding week.
    allowed_start = week_start - pd.Timedelta(days=7)
    if end < allowed_start or start > week_end:
        return VerificationResult(False, "date_window_mismatch")
    if not _direction_is_increase(note.text):
        return VerificationResult(False, "not_an_explicit_cost_increase")
    if not _plausible_cause(note.text):
        return VerificationResult(False, "implausible_or_unknown_cause")
    return VerificationResult(True, "verified")


def select_supporting_note(candidates: list[RetrievedNote], route: str,
                           week_of: str | pd.Timestamp) -> tuple[RetrievedNote | None, str]:
    """Select highest-ranked verified note, deterministically tie-breaking by ID."""
    passing = [n for n in candidates if verify_note(n, route, week_of).supported]
    if not passing:
        return None, "unexplained"
    passing.sort(key=lambda n: (-n.score, n.note_id))
    return passing[0], "justified"
