"""Hand-computed tests for core weekly logic and baselines."""
import pandas as pd
import pytest
from watchdog.weekly import monday_of_week, build_weekly_costs
from watchdog.baselines import add_baselines
from watchdog.flags import apply_flags


def test_monday_bucket_sunday_and_monday_boundary():
    dates = pd.Series(pd.to_datetime(["2024-01-07", "2024-01-08"]))
    assert list(monday_of_week(dates).dt.strftime("%Y-%m-%d")) == ["2024-01-01", "2024-01-08"]


def weekly_fixture(values):
    return pd.DataFrame({
        "origin": ["A"] * len(values), "destination": ["B"] * len(values),
        "route_type": ["Short"] * len(values),
        "week_of": pd.to_datetime(["2024-01-01"] + [f"2024-01-{1 + 7*i:02d}" for i in range(1, len(values))]),
        "cost_per_tonne_km": values,
    })


def test_history_is_strictly_prior_and_no_lookahead():
    weekly = weekly_fixture([2.0, 4.0, 8.0])
    result = add_baselines(weekly, history_weeks=8)
    assert pd.isna(result.loc[0, "own_history_avg"])
    assert result.loc[1, "own_history_avg"] == pytest.approx(2.0)
    assert result.loc[2, "own_history_avg"] == pytest.approx(3.0)
    # Changing a future value cannot affect an earlier baseline.
    changed = weekly.copy(); changed.loc[2, "cost_per_tonne_km"] = 8000.0
    changed_result = add_baselines(changed, history_weeks=8)
    assert changed_result.loc[1, "own_history_avg"] == pytest.approx(result.loc[1, "own_history_avg"])


def test_fewer_than_eight_prior_weeks_uses_available_weeks():
    result = add_baselines(weekly_fixture([1.0, 2.0, 3.0]), history_weeks=8)
    assert result["own_history_weeks_used"].tolist() == [0, 1, 2]
    assert result.loc[2, "own_history_avg"] == pytest.approx(1.5)


def test_peer_average_excludes_current_route():
    frame = pd.DataFrame({
        "origin": ["A", "C", "E"], "destination": ["B", "D", "F"],
        "route_type": ["Short"] * 3, "week_of": pd.to_datetime(["2024-01-01"] * 3),
        "cost_per_tonne_km": [2.0, 4.0, 6.0],
    })
    result = add_baselines(frame)
    assert result.loc[result.origin.eq("A"), "peer_avg"].iloc[0] == pytest.approx(5.0)
    assert result.loc[result.origin.eq("C"), "peer_avg"].iloc[0] == pytest.approx(4.0)


def test_weekly_aggregation_is_ratio_of_sums():
    shipments = pd.DataFrame({
        "origin": ["A", "A"], "destination": ["B", "B"], "route_type": ["Short", "Short"],
        "shipment_date": pd.to_datetime(["2024-01-01", "2024-01-07"]),
        "quantity_tonnes": [1.0, 3.0], "distance_km": [10.0, 10.0],
        "freight_cost_inr": [100.0, 300.0], "shipment_id": ["1", "2"],
    })
    result = build_weekly_costs(shipments)
    assert len(result) == 1
    assert result.loc[0, "cost_per_tonne_km"] == pytest.approx(10.0)
    assert result.loc[0, "shipment_count"] == 2


def test_no_history_means_cannot_be_flagged():
    frame = pd.DataFrame({
        "cost_per_tonne_km": [10.0], "previous_week_cost": [None], "own_history_avg": [None],
        "peer_avg": [5.0], "own_history_z_score": [None],
    })
    assert not bool(apply_flags(frame).loc[0, "flagged_bool"])
