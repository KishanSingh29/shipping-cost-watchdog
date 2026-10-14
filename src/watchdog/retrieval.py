"""Deterministic retrieval of context notes for flagged route-weeks.

Uses TF-IDF retrieval as a lightweight, local baseline. The verification gate in
verify.py, not the retrieval score, determines whether a note can be cited.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass(frozen=True)
class RetrievedNote:
    """A retrieved note and its deterministic similarity score."""
    note_id: str
    date: pd.Timestamp
    applies_to: str
    text: str
    score: float


def _clean(value: object) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(value).lower()).strip()


def retrieve_notes(notes: pd.DataFrame, route: str, week_of: str | pd.Timestamp,
                   material: str = "", top_k: int = 5) -> list[RetrievedNote]:
    """Rank notes by TF-IDF similarity; ties are broken by note_id.

    The note schema is the supplied context_notes.csv schema: note_id, date,
    applies_to, note. Metadata verification happens separately.
    """
    required = {"note_id", "date", "applies_to", "note"}
    missing = required - set(notes.columns)
    if missing:
        raise ValueError(f"Context notes missing columns: {sorted(missing)}")
    if notes.empty:
        return []
    query = f"{route} {material} week starting {pd.Timestamp(week_of).date()} freight cost increase surcharge fuel toll weather festival"
    corpus = (notes["applies_to"].fillna("").astype(str) + " " +
              notes["note"].fillna("").astype(str)).tolist()
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), lowercase=True, norm="l2")
    matrix = vectorizer.fit_transform(corpus + [query])
    scores = cosine_similarity(matrix[-1], matrix[:-1]).ravel()
    ranked = sorted(range(len(notes)), key=lambda i: (-float(scores[i]), str(notes.iloc[i]["note_id"])))
    result = []
    for i in ranked[:max(0, top_k)]:
        row = notes.iloc[i]
        result.append(RetrievedNote(str(row["note_id"]), pd.Timestamp(row["date"]),
                                    str(row["applies_to"]), str(row["note"]), float(scores[i])))
    return result


def retrieve_notes_semantic(notes: pd.DataFrame, route: str, week_of: str | pd.Timestamp,
                            material: str = "", top_k: int = 5,
                            model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> list[RetrievedNote]:
    """Optional local semantic retrieval using a pinned sentence-transformers model.

    This requires installing sentence-transformers and downloading the model once.
    The default pipeline uses TF-IDF to avoid a large model download during the
    24-hour assessment; this function makes semantic retrieval an explicit opt-in.
    """
    try:
        from sentence_transformers import SentenceTransformer
        import numpy as np
    except ImportError as exc:
        raise RuntimeError("Semantic retrieval requires sentence-transformers; install it first.") from exc
    required = {"note_id", "date", "applies_to", "note"}
    missing = required - set(notes.columns)
    if missing:
        raise ValueError(f"Context notes missing columns: {sorted(missing)}")
    if notes.empty:
        return []
    query = f"Route: {route}. Material: {material}. Week: {pd.Timestamp(week_of).date()}. Shipping cost increase due to fuel, toll, weather, or festival."
    documents = [f"Route scope: {r.applies_to}. Note: {r.note}" for r in notes.itertuples(index=False)]
    model = SentenceTransformer(model_name)
    vectors = model.encode(documents + [query], normalize_embeddings=True, convert_to_numpy=True,
                           show_progress_bar=False)
    scores = np.matmul(vectors[:-1], vectors[-1])
    ranked = sorted(range(len(notes)), key=lambda i: (-float(scores[i]), str(notes.iloc[i]["note_id"])))
    return [RetrievedNote(str(notes.iloc[i]["note_id"]), pd.Timestamp(notes.iloc[i]["date"]),
                          str(notes.iloc[i]["applies_to"]), str(notes.iloc[i]["note"]), float(scores[i]))
            for i in ranked[:max(0, top_k)]]
