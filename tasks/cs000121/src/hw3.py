# hw3.py
from __future__ import annotations

from typing import List, Dict, Any
import numpy as np
import pandas as pd


# ---------- Part A: Lookup tables (age / residence) ----------

def read_age_classes(path: str, sep: str = " ") -> pd.DataFrame:
    """
    Read age_classes.txt into a DataFrame with columns ['code', 'age_range'].

    The file uses a single-character delimiter (default: space).
    Do NOT coerce dtypes here; just name the columns.
    """
    # TODO: implement using pd.read_csv with header=None and names=['code','age_range']
    raise NotImplementedError("TODO: implement read_age_classes")


def coerce_age_range_ordered(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ensure df['age_range'] is an *ordered* categorical (ordinal).
    Return a new DataFrame (do not mutate the input in place).
    """
    # TODO: implement by copying df and setting astype('category') with ordered=True
    raise NotImplementedError("TODO: implement coerce_age_range_ordered")


def add_age_min_max(df: pd.DataFrame) -> pd.DataFrame:
    """
    From an 'age_range' like '30-34', derive integer columns 'age_min' and 'age_max'.
    Return a new DataFrame with the added columns.
    """
    # TODO: implement via .str.split('-', expand=True).astype(int)
    raise NotImplementedError("TODO: implement add_age_min_max")


def add_age_center(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add a float column 'age_center' = (age_min + age_max) / 2.0.
    Assumes age_min/age_max already exist.
    Return a new DataFrame.
    """
    # TODO: implement without mutating the input
    raise NotImplementedError("TODO: implement add_age_center")


def read_residence_areas(path: str, delimiter: str = ":") -> pd.DataFrame:
    """
    Read residence_area.txt into a DataFrame with columns ['code','area'].
    Strip leading/trailing whitespace in 'area'.
    """
    # TODO: implement using pd.read_csv(..., delimiter=delimiter, header=None, names=[...])
    raise NotImplementedError("TODO: implement read_residence_areas")


def assign_dist_rank(df: pd.DataFrame, ranks: List[float | int | None]) -> pd.DataFrame:
    """
    Add a 'dist_rank' column from a provided list (same length as df).
    Use np.nan for missing values (when element is None).
    Return a new DataFrame.
    """
    # TODO: implement
    raise NotImplementedError("TODO: implement assign_dist_rank")


# ---------- Part B: Ta-Feng core table utilities ----------

TAFENG_COLUMNS = [
    'transaction_time', 'customer_id', 'age_class', 'residence_area',
    'product_subclass', 'product_id', 'amount', 'asset', 'sales_price'
]


def normalize_keys(taFeng: pd.DataFrame) -> pd.DataFrame:
    """
    Trim hard-to-detect whitespace in 'age_class' and 'residence_area'.
    Return a new DataFrame.
    """
    # TODO: implement using .str.strip() on those two columns
    raise NotImplementedError("TODO: implement normalize_keys")


def join_lookup_tables(taFeng: pd.DataFrame,
                       age_classes: pd.DataFrame,
                       residence_areas: pd.DataFrame) -> pd.DataFrame:
    """
    Left-join taFeng with age_classes (key: left 'age_class' -> right 'code'),
    then left-join with residence_areas (key: left 'residence_area' -> right 'code').
    Use suffixes ['_age', '_residence'] for the two joins.
    """
    # TODO: implement with pd.merge(... how='left' ...)
    raise NotImplementedError("TODO: implement join_lookup_tables")


def have_same_nrows(df1: pd.DataFrame, df2: pd.DataFrame) -> bool:
    """
    Return True iff df1 and df2 have the same number of rows.
    """
    # TODO: implement
    raise NotImplementedError("TODO: implement have_same_nrows")


# ---------- Part C: EDA helpers (repeat business, carts, time) ----------

def count_trips_per_customer(taFeng: pd.DataFrame) -> pd.Series:
    """
    Count shopping trips per customer over the period.

    Treat all purchases by the same customer on the *same calendar day*
    as one trip (i.e., collapse to date). Return a Series indexed by
    customer_id, with integer counts.
    """
    # TODO: implement by converting transaction_time to datetime, using .dt.date, then groupby nunique
    raise NotImplementedError("TODO: implement count_trips_per_customer")


def compute_deciles(values: pd.Series) -> pd.Series:
    """
    Return deciles (0.0, 0.1, ..., 1.0) via Series.quantile with np.arange(0,1.1,0.1).
    """
    # TODO: implement
    raise NotImplementedError("TODO: implement compute_deciles")


def build_carts(taFengFull: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate item-level rows into shopping carts at (customer_id, transaction_time).

    Output DataFrame must contain:
      - 'num_items' : sum of 'amount'
      - 'num_unique': count of rows in the cart (use .count() over 'amount')
      - 'total'     : sum of 'sales_price'
    Keep the index as a MultiIndex on (customer_id, transaction_time) or reset it—either is fine.
    """
    # TODO: implement with groupby on ['customer_id','transaction_time']
    raise NotImplementedError("TODO: implement build_carts")


def unique_customers_per_day(taFengFull: pd.DataFrame) -> pd.Series:
    """
    Return a Series indexed by date (normalized to day) with the number of unique customers per day.
    """
    # TODO: implement (convert to datetime; groupby date; nunique over customer_id)
    raise NotImplementedError("TODO: implement unique_customers_per_day")


DAY_OF_WEEK_ORDER = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']


def add_day_of_week_and_week(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add:
      - 'day_of_week': ordered categorical with DAY_OF_WEEK_ORDER
      - 'week_of_year': ISO week number (integer)

    Requires df['transaction_time'] to be datetime-like.
    Return a new DataFrame.
    """
    # TODO: implement using .dt.day_name() and .dt.isocalendar().week (or fallback)
    raise NotImplementedError("TODO: implement add_day_of_week_and_week")


def count_by_weekday(df: pd.DataFrame) -> pd.DataFrame:
    """
    Reproduce the 'count_by_weekday' table:

      - Deduplicate daily visits by (week_of_year, day_of_week, customer_id, transaction_time)
      - Group by ['day_of_week','week_of_year'] and count rows
      - Return a DataFrame with columns ['day_of_week','week_of_year','count']
    """
    # TODO: implement
    raise NotImplementedError("TODO: implement count_by_weekday")