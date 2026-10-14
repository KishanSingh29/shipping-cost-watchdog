import pandas as pd
from watchdog.retrieval import RetrievedNote, retrieve_notes
from watchdog.verify import verify_note, select_supporting_note


def note(note_id, date, applies_to, text, score=0.5):
    return RetrievedNote(note_id, pd.Timestamp(date), applies_to, text, score)


def test_flood_note_supports_chennai_week_of_feb_24():
    candidate = note("N001", "2025-02-24", "Chennai-Bangalore",
                     "Heavy flooding on the Chennai-Bangalore highway disrupted normal truck movement from Feb 24 to Mar 8, forcing longer detours and higher trip costs. Roads were passable again by Mar 9.")
    assert verify_note(candidate, "Chennai-Bangalore", "2025-02-24").supported


def test_flood_note_does_not_support_week_after_recovery():
    candidate = note("N001", "2025-02-24", "Chennai-Bangalore",
                     "Heavy flooding on the Chennai-Bangalore highway disrupted normal truck movement from Feb 24 to Mar 8, forcing longer detours and higher trip costs. Roads were passable again by Mar 9.")
    assert not verify_note(candidate, "Chennai-Bangalore", "2025-03-10").supported


def test_wrong_route_rejected():
    candidate = note("N002", "2025-01-20", "Ahmedabad-Mumbai",
                     "A regional festival week saw a temporary surcharge applied by transporters on the Ahmedabad-Mumbai corridor due to high demand and limited truck availability.")
    assert verify_note(candidate, "Delhi-Jaipur", "2025-01-20").reason == "route_scope_mismatch"


def test_negative_note_rejected():
    candidate = note("N005", "2024-07-29", "Mumbai-Delhi",
                     "Scheduled highway maintenance work between Mumbai and Delhi caused minor delays for about a week; costs were not significantly affected.")
    assert not verify_note(candidate, "Mumbai-Delhi", "2024-07-29").supported


def test_all_routes_diesel_increase_supported_after_start():
    candidate = note("N003", "2025-05-05", "All Routes",
                     "Diesel prices rose nationwide starting this week, pushing up transportation costs across all routes by roughly 5-7%.")
    assert verify_note(candidate, "Mumbai-Delhi", "2025-05-12").supported


def test_no_verified_note_means_unexplained():
    wrong = note("N002", "2025-01-20", "Ahmedabad-Mumbai",
                 "A regional festival week saw a temporary surcharge applied by transporters on the Ahmedabad-Mumbai corridor due to high demand and limited truck availability.")
    selected, verdict = select_supporting_note([wrong], "Delhi-Jaipur", "2025-01-20")
    assert selected is None
    assert verdict == "unexplained"


def test_retrieval_is_deterministic_and_has_expected_schema():
    notes = pd.DataFrame([
        {"note_id": "N002", "date": "2025-01-20", "applies_to": "Ahmedabad-Mumbai", "note": "festival surcharge"},
        {"note_id": "N001", "date": "2025-02-24", "applies_to": "Chennai-Bangalore", "note": "flood detour higher trip costs"},
    ])
    first = retrieve_notes(notes, "Chennai-Bangalore", "2025-02-24", top_k=2)
    second = retrieve_notes(notes, "Chennai-Bangalore", "2025-02-24", top_k=2)
    assert [(n.note_id, n.score) for n in first] == [(n.note_id, n.score) for n in second]
    assert first[0].note_id == "N001"
