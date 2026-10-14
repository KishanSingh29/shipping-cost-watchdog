import sys
import types
import numpy as np
import pandas as pd
from watchdog.retrieval import retrieve_notes_semantic


class FakeModel:
    def __init__(self, name):
        self.name = name
    def encode(self, texts, **kwargs):
        # Deterministic toy embeddings: route-specific text gets higher similarity.
        return np.array([[1.0, 0.0] if "Chennai-Bangalore" in text else [0.0, 1.0]
                         for text in texts], dtype=float)


def test_semantic_retrieval_ranks_relevant_note_and_breaks_ties(monkeypatch):
    module = types.ModuleType("sentence_transformers")
    module.SentenceTransformer = FakeModel
    monkeypatch.setitem(sys.modules, "sentence_transformers", module)
    notes = pd.DataFrame([
        {"note_id": "N002", "date": "2025-01-20", "applies_to": "Ahmedabad-Mumbai", "note": "festival surcharge"},
        {"note_id": "N001", "date": "2025-02-24", "applies_to": "Chennai-Bangalore", "note": "flood detour higher trip costs"},
    ])
    # Fake query vector is the final vector; first note is intentionally irrelevant.
    result = retrieve_notes_semantic(notes, "Chennai-Bangalore", "2025-02-24", top_k=2)
    assert result[0].note_id == "N001"
    assert result[0].score == 1.0
