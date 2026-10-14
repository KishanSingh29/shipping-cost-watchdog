"""Input loading and validation."""
from pathlib import Path
import pandas as pd

SHIPMENT_COLUMNS = {
    "shipment_id", "origin", "destination", "route_type", "material",
    "quantity_tonnes", "distance_km", "freight_cost_inr", "shipment_date", "transporter",
}


def load_shipments(path: str | Path) -> pd.DataFrame:
    """Load shipments, validate required fields and reject invalid records explicitly."""
    frame = pd.read_csv(path)
    missing = SHIPMENT_COLUMNS - set(frame.columns)
    if missing:
        raise ValueError(f"Missing shipment columns: {sorted(missing)}")
    frame = frame.copy()
    for col in ["shipment_id", "origin", "destination", "route_type", "material", "transporter"]:
        frame[col] = frame[col].astype("string").str.strip()
    frame["shipment_date"] = pd.to_datetime(frame["shipment_date"], errors="coerce")
    numeric = ["quantity_tonnes", "distance_km", "freight_cost_inr"]
    for col in numeric:
        frame[col] = pd.to_numeric(frame[col], errors="coerce")
    invalid = frame["shipment_date"].isna() | frame[numeric].isna().any(axis=1)
    invalid |= (frame[numeric] <= 0).any(axis=1)
    invalid |= frame[["origin", "destination", "route_type", "shipment_id"]].isna().any(axis=1)
    invalid |= frame[["origin", "destination", "route_type", "shipment_id"]].eq("").any(axis=1)
    if invalid.any():
        bad_ids = frame.loc[invalid, "shipment_id"].astype(str).tolist()
        raise ValueError(f"Invalid shipment rows ({len(bad_ids)}); no rows silently dropped. IDs: {bad_ids[:20]}")
    allowed = {"Short", "Medium", "Long"}
    unknown = sorted(set(frame["route_type"].dropna()) - allowed)
    if unknown:
        raise ValueError(f"Unexpected route_type values: {unknown}")
    if frame["shipment_id"].duplicated().any():
        raise ValueError("Duplicate shipment_id values found")
    return frame
