"""Deterministic anomaly flag rules."""
import pandas as pd


def apply_flags(
    frame: pd.DataFrame,
    own_history_increase_pct: float = 0.10,
    peer_increase_pct: float = 0.10,
    own_history_z_score: float = 2.0,
) -> pd.DataFrame:
    """Flag increases that beat last week, history, and either peer or z-score criteria."""
    result = frame.copy()
    current = pd.to_numeric(result["cost_per_tonne_km"], errors="coerce")
    previous = pd.to_numeric(result["previous_week_cost"], errors="coerce")
    history = pd.to_numeric(result["own_history_avg"], errors="coerce")
    peers = pd.to_numeric(result["peer_avg"], errors="coerce")
    z_score = pd.to_numeric(result["own_history_z_score"], errors="coerce")
    history_rise = current > history * (1 + own_history_increase_pct)
    peer_rise = current > peers * (1 + peer_increase_pct)
    z_rise = z_score > own_history_z_score
    result["flagged_bool"] = (
        result["previous_week_cost"].notna()
        & result["own_history_avg"].notna()
        & result["peer_avg"].notna()
        & (current > previous)
        & history_rise
        & (peer_rise | z_rise.fillna(False))
    )
    return result
