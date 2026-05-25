from __future__ import annotations
from typing import Iterable, Tuple, Optional
from pathlib import Path
import numpy as np
import pandas as pd


# -------------------------
# I/O helpers (optional)
# -------------------------

def load_csv(path: str | Path, **kwargs) -> pd.DataFrame:
    return pd.read_csv(path, **kwargs)


def save_csv(df: pd.DataFrame, path: str | Path) -> Path:
    p = Path(path)
    df.to_csv(p, index=False)
    return p


# -------------------------
# Core functions (fill TODOs)
# -------------------------

def extract_hour(time: pd.Series | np.ndarray | float | int) -> pd.Series | np.ndarray | float | int:
    """
    Extracts hour from military time (e.g., 1303.0 -> 13).
    Works with scalars, numpy arrays, or pandas Series of dtype float64/int64.
    """
    # TODO: implement using integer division by 100, preserving input container type
    raise NotImplementedError


def extract_mins(time: pd.Series | np.ndarray | float | int) -> pd.Series | np.ndarray | float | int:
    """
    Extracts minutes from military time (e.g., 1303.0 -> 3).
    Works with scalars, numpy arrays, or pandas Series.
    """
    # TODO: implement using modulo 100, preserving input container type
    raise NotImplementedError


def convert_to_minofday(time: pd.Series | np.ndarray | float | int) -> pd.Series | np.ndarray | float | int:
    """
    Converts military time to minutes since 00:00. Example: 13:03 -> 783.
    """
    # TODO: use extract_hour and extract_mins and return hour*60 + mins
    raise NotImplementedError


def calc_time_diff(x_sched: pd.Series | np.ndarray,
                   y_actual: pd.Series | np.ndarray) -> pd.Series | np.ndarray:
    """
    Returns delay minutes = actual - scheduled, both in military time.
    """
    # TODO: convert both to minutes-of-day then subtract
    raise NotImplementedError


def filter_delayed15(flights: pd.DataFrame,
                     sched_col: str = "sched_dep_time",
                     actual_col: str = "actual_dep_time") -> pd.DataFrame:
    """
    Filters flights with departure delay > 15 minutes.
    """
    # TODO: compute delay via calc_time_diff and return filtered df
    raise NotImplementedError


def delayed_dest_cities(delayed_flights: pd.DataFrame,
                        airports: pd.DataFrame,
                        flights_dest_col: str = "destination",
                        airports_code_col: str = "iata",
                        airports_city_col: str = "city") -> pd.Series:
    """
    Returns alphabetically sorted Series of city names for delayed destinations.
    """
    # TODO: join on IATA code and return sorted cities (duplicates removed)
    raise NotImplementedError


def top10_tailnums_by_unique_destinations(flights: pd.DataFrame,
                                          tail_col: str = "tailnum",
                                          dest_col: str = "destination") -> pd.Series:
    """
    Returns a Series indexed by tailnum with counts of unique destinations, top 10.
    """
    # TODO: drop duplicates on (tail,dest), groupby tail, size, sort desc, head 10
    raise NotImplementedError


def add_sfo_arr_delay_avg(airports: pd.DataFrame,
                          flights: pd.DataFrame,
                          origin_col: str = "origin",
                          sched_col: str = "sched_dep_time",
                          actual_col: str = "actual_dep_time",
                          dest_col: str = "destination",
                          airports_code_col: str = "iata",
                          out_col: str = "sfo_arr_delay_avg") -> pd.DataFrame:
    """
    Adds a column to airports with average departure delay from SFO grouped by destination.
    Returns a new DataFrame (does not modify in place).
    """
    # TODO: compute delay; group SFO flights by destination mean; merge to airports; rename to out_col
    raise NotImplementedError


# -------------------------
# Optional utilities
# -------------------------

def load_optional_flights_and_airports(flights_path: str | Path,
                                       airports_path: str | Path,
                                       airports_cols: Optional[Iterable[str]] = None
                                       ) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Optional convenience for reading external datasets if available.
    """
    flights = pd.read_csv(flights_path)
    if airports_cols is None:
        airports = pd.read_csv(airports_path)
    else:
        airports = pd.read_csv(airports_path, names=list(airports_cols))
    return flights, airports