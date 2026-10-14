"""Historical and peer comparison baselines."""
import numpy as np
import pandas as pd
from .weekly import ROUTE_KEYS


def add_baselines(weekly: pd.DataFrame, history_weeks: int = 8) -> pd.DataFrame:
    """Add strictly-prior own-history and same-week same-type peer baselines."""
    if history_weeks < 1:
        raise ValueError("history_weeks must be >= 1")
    frame = weekly.sort_values(ROUTE_KEYS + ["week_of"]).copy()
    grouped = frame.groupby(ROUTE_KEYS, sort=False)["cost_per_tonne_km"]
    frame["previous_week_cost"] = grouped.shift(1)
    # shift first: the current week's value cannot leak into its own baseline.
    frame["own_history_avg"] = grouped.transform(
        lambda values: values.shift(1).rolling(history_weeks, min_periods=1).mean()
    )
    frame["own_history_std"] = grouped.transform(
        lambda values: values.shift(1).rolling(history_weeks, min_periods=2).std(ddof=0)
    )
    frame["own_history_weeks_used"] = grouped.transform(
        lambda values: values.shift(1).rolling(history_weeks, min_periods=1).count()
    ).fillna(0).astype(int)
    # Peers are other route groups with the same route_type in the same week.
    peer_group = frame.groupby(["route_type", "week_of"])["cost_per_tonne_km"]
    frame["peer_route_count"] = peer_group.transform("count") - 1
    frame["peer_avg"] = peer_group.transform("sum")
    frame["peer_avg"] = np.where(
        frame["peer_route_count"] > 0,
        (frame["peer_avg"] - frame["cost_per_tonne_km"]) / frame["peer_route_count"],
        np.nan,
    )
    frame["vs_own_history_pct"] = (frame["cost_per_tonne_km"] / frame["own_history_avg"] - 1) * 100
    frame["vs_similar_routes_pct"] = (frame["cost_per_tonne_km"] / frame["peer_avg"] - 1) * 100
    frame["own_history_z_score"] = np.where(
        frame["own_history_std"] > 0,
        (frame["cost_per_tonne_km"] - frame["own_history_avg"]) / frame["own_history_std"],
        np.nan,
    )
    return frame.sort_values(["week_of"] + ROUTE_KEYS).reset_index(drop=True)
