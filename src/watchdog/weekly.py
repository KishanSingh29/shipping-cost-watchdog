"""Weekly route-level cost calculations."""
import pandas as pd

ROUTE_KEYS = ["origin", "destination", "route_type"]


def monday_of_week(dates: pd.Series) -> pd.Series:
    """Return Monday date for each date; Monday stays in the same week."""
    parsed = pd.to_datetime(dates)
    return (parsed - pd.to_timedelta(parsed.dt.weekday, unit="D")).dt.normalize()


def build_weekly_costs(shipments: pd.DataFrame) -> pd.DataFrame:
    """Aggregate by directed route and Monday week using ratio of sums."""
    frame = shipments.copy()
    frame["week_of"] = monday_of_week(frame["shipment_date"])
    frame["quantity_distance"] = frame["quantity_tonnes"] * frame["distance_km"]
    grouped = frame.groupby(ROUTE_KEYS + ["week_of"], as_index=False, sort=True).agg(
        total_cost=("freight_cost_inr", "sum"),
        total_quantity_distance=("quantity_distance", "sum"),
        shipment_count=("shipment_id", "count"),
    )
    grouped["cost_per_tonne_km"] = grouped["total_cost"] / grouped["total_quantity_distance"]
    return grouped.sort_values(ROUTE_KEYS + ["week_of"]).reset_index(drop=True)
