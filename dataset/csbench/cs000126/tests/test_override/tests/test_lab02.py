from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

import lab02 as stu


# -------------------------
# Reference implementations
# -------------------------

def _ref_extract_hour(x):
    if isinstance(x, (int, float, np.floating, np.integer)):
        return int(x) // 100
    arr = pd.Series(x) if isinstance(x, (list, tuple, np.ndarray)) else x
    out = (arr.astype("float64") // 100).astype(int)
    return out.values if not isinstance(x, pd.Series) else out

def _ref_extract_mins(x):
    if isinstance(x, (int, float, np.floating, np.integer)):
        return int(x) % 100
    arr = pd.Series(x) if isinstance(x, (list, tuple, np.ndarray)) else x
    out = (arr.astype("float64") % 100).astype(int)
    return out.values if not isinstance(x, pd.Series) else out

def _ref_convert_to_minofday(x):
    h = _ref_extract_hour(x)
    m = _ref_extract_mins(x)
    if isinstance(h, (int, float, np.floating, np.integer)):
        return h * 60 + m
    return (pd.Series(h).astype(int) * 60 + pd.Series(m).astype(int)).values

def _ref_calc_time_diff(x, y):
    return _ref_convert_to_minofday(y) - _ref_convert_to_minofday(x)


# -------------------------
# Synthetic fixtures
# -------------------------

@pytest.fixture
def flights_small() -> pd.DataFrame:
    return pd.DataFrame({
        "origin": ["SFO", "SFO", "OAK", "SFO", "OAK"],
        "destination": ["LAX", "SEA", "LAX", "JFK", "SEA"],
        "sched_dep_time": [900.0, 1303.0, 755.0, 2230.0, 600.0],
        "actual_dep_time": [915.0, 1325.0, 800.0, 2248.0, 559.0],
        "tailnum": ["N1", "N2", "N1", "N3", "N1"],
    })

@pytest.fixture
def airports_small() -> pd.DataFrame:
    return pd.DataFrame({
        "iata": ["LAX", "SEA", "JFK", "SFO"],
        "city": ["Los Angeles", "Seattle", "New York", "San Francisco"],
        "name": ["Los Angeles Intl", "Seattle-Tacoma", "JFK", "SFO"],
    })


# -------------------------
# Unit tests: time parsing
# -------------------------

def test_extract_hour_scalar_and_array():
    try:
        h1 = stu.extract_hour(1303.0)
    except NotImplementedError:
        pytest.skip("extract_hour not implemented")
    assert h1 == 13
    arr = np.array([0.0, 59.0, 100.0, 2359.0])
    h = stu.extract_hour(arr)
    np.testing.assert_array_equal(h, _ref_extract_hour(arr))

def test_extract_mins_scalar_and_series():
    try:
        m1 = stu.extract_mins(1303.0)
    except NotImplementedError:
        pytest.skip("extract_mins not implemented")
    assert m1 == 3
    s = pd.Series([0.0, 59.0, 100.0, 2359.0])
    m = stu.extract_mins(s)
    pd.testing.assert_series_equal(m, _ref_extract_mins(s))

def test_convert_to_minofday_example():
    try:
        val = stu.convert_to_minofday(1303.0)
    except NotImplementedError:
        pytest.skip("convert_to_minofday not implemented")
    assert val == 783.0


# -------------------------
# Unit tests: delays and filtering
# -------------------------

def test_calc_time_diff_vectorized(flights_small):
    try:
        d = stu.calc_time_diff(flights_small["sched_dep_time"], flights_small["actual_dep_time"])
    except NotImplementedError:
        pytest.skip("calc_time_diff not implemented")
    ref = _ref_calc_time_diff(flights_small["sched_dep_time"], flights_small["actual_dep_time"])
    np.testing.assert_array_equal(np.asarray(d), np.asarray(ref))

def test_filter_delayed15(flights_small):
    try:
        delayed = stu.filter_delayed15(flights_small)
    except NotImplementedError:
        pytest.skip("filter_delayed15 not implemented")
    assert set(delayed["destination"]) == {"LAX", "SEA", "JFK"}
    assert len(delayed) == 3


# -------------------------
# Unit tests: joins and counts
# -------------------------

def test_delayed_dest_cities(flights_small, airports_small):
    try:
        delayed = stu.filter_delayed15(flights_small)
        cities = stu.delayed_dest_cities(delayed, airports_small)
    except NotImplementedError:
        pytest.skip("join-related functions not implemented")
    assert list(cities) == ["Los Angeles", "New York", "Seattle"]

def test_top10_tailnums_by_unique_destinations(flights_small):
    try:
        top = stu.top10_tailnums_by_unique_destinations(flights_small)
    except NotImplementedError:
        pytest.skip("top10 function not implemented")
    # N1 flew to 2 unique destinations, N2 and N3 to 1
    assert top.index[0] == "N1"
    assert top.iloc[0] == 2
    assert set(top.index[1:]) == {"N2", "N3"}


# -------------------------
# Unit tests: aggregate and merge back
# -------------------------

def test_add_sfo_arr_delay_avg(flights_small, airports_small):
    try:
        out = stu.add_sfo_arr_delay_avg(airports_small, flights_small)
    except NotImplementedError:
        pytest.skip("add_sfo_arr_delay_avg not implemented")
    assert "sfo_arr_delay_avg" in out.columns
    # SFO origin to LAX delay: 15, to SEA delay: 22, to JFK delay: 18
    row_lax = out[out["iata"] == "LAX"]["sfo_arr_delay_avg"].iloc[0]
    row_sea = out[out["iata"] == "SEA"]["sfo_arr_delay_avg"].iloc[0]
    row_jfk = out[out["iata"] == "JFK"]["sfo_arr_delay_avg"].iloc[0]
    assert row_lax == 15
    assert row_sea == 22
    assert row_jfk == 18

# -------------------------
# External-file tests (required; files must exist in CWD)
# -------------------------

def test_external_files_present_and_used():
    flights_path, airports_path = "flights.dat", "airports.dat"

    # Airports file has fixed columns per assignment handout
    airports_cols = [
        'openflights_id','name','city','country','iata','icao',
        'latitude','longitude','altitude','tz','dst','tz_olson','type','airport_dsource'
    ]
    flights, airports = stu.load_optional_flights_and_airports(
        flights_path, airports_path, airports_cols=airports_cols
    )

    # Basic schema checks
    need_f_cols = {"sched_dep_time", "actual_dep_time", "origin", "destination"}
    need_a_cols = {"iata", "city"}
    assert need_f_cols.issubset(flights.columns), f"Missing columns in flights: {need_f_cols - set(flights.columns)}"
    assert need_a_cols.issubset(airports.columns), f"Missing columns in airports: {need_a_cols - set(airports.columns)}"

    # 1) filter_delayed15 should match a reference computation
    ref_delay = _ref_calc_time_diff(flights["sched_dep_time"], flights["actual_dep_time"])
    ref_mask = pd.Series(ref_delay >= 15, index=flights.index)
    delayed = stu.filter_delayed15(flights.copy())
    assert isinstance(delayed, pd.DataFrame)
    assert set(delayed.index) == set(flights.index[ref_mask]), "Delayed filter mismatch vs reference"

    # 2) delayed_dest_cities smoke + type checks
    cities = stu.delayed_dest_cities(delayed, airports)
    assert isinstance(cities, (pd.Series, list, np.ndarray))
    if isinstance(cities, pd.Series):
        assert all(isinstance(x, str) for x in cities.tolist())
    else:
        assert all(isinstance(x, str) for x in list(cities))

    # 3) top10_tailnums_by_unique_destinations sanity
    top = stu.top10_tailnums_by_unique_destinations(flights)
    assert isinstance(top, pd.Series)
    assert len(top) <= 10
    assert all(int(c) >= 1 for c in top.values)

    # 4) add_sfo_arr_delay_avg should equal groupby-mean after merge (on intersection)
    out = stu.add_sfo_arr_delay_avg(airports.copy(), flights.copy(), out_col="sfo_arr_delay_avg")
    assert "sfo_arr_delay_avg" in out.columns

    ref_df = flights.copy()
    ref_df["delay"] = _ref_calc_time_diff(ref_df["sched_dep_time"], ref_df["actual_dep_time"])
    ref_mean = (ref_df[ref_df["origin"] == "SFO"]
                .groupby("destination")["delay"].mean())

    merged = out.set_index("iata")["sfo_arr_delay_avg"]
    inter = ref_mean.index.intersection(merged.index)
    if len(inter) > 0:
        diff = (merged[inter] - ref_mean[inter]).abs()
        mask = (~merged[inter].isna()) & (~ref_mean[inter].isna())
        assert (diff[mask] <= 1e-9).all(), "SFO mean delay merge mismatch"