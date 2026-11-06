# Homework 3 — Data Wrangling and Exploratory Data Analysis (Refactor from Notebook)

## Goal
Turn the original notebook into a clean Python module and implement utilities for reading lookup tables, joining them to the Ta-Feng transaction table, computing per-customer trip counts, aggregating carts, and preparing time-series features for exploratory plots.

## What You Must Implement
Edit **`hw3.py`** and complete every **TODO**:

### A. Lookup Tables
- `read_age_classes(path, sep=" ") -> pd.DataFrame`  
  Read `age_classes.txt` into columns `['code','age_range']`.
- `coerce_age_range_ordered(df) -> pd.DataFrame`  
  Make `age_range` an **ordered** categorical (ordinal).
- `add_age_min_max(df) -> pd.DataFrame`  
  Add integer `age_min`, `age_max` parsed from `age_range`.
- `add_age_center(df) -> pd.DataFrame`  
  Add `age_center = (age_min + age_max) / 2.0`.
- `read_residence_areas(path, delimiter=":") -> pd.DataFrame`  
  Read `residence_area.txt` into `['code','area']` and strip whitespace.
- `assign_dist_rank(df, ranks) -> pd.DataFrame`  
  Add `dist_rank` from a provided list; use `np.nan` for missing.

### B. Ta-Feng Core & Joins
- `normalize_keys(taFeng) -> pd.DataFrame`  
  Strip whitespace in `age_class` and `residence_area`.
- `join_lookup_tables(taFeng, age_classes, residence_areas) -> pd.DataFrame`  
  Left-join the lookups (suffixes `['_age', '_residence']`).
- `have_same_nrows(df1, df2) -> bool`

### C. EDA Helpers
- `count_trips_per_customer(taFeng) -> pd.Series`  
  Treat all purchases by the same customer on the **same day** as one trip; return counts per `customer_id`.
- `compute_deciles(values) -> pd.Series`  
  Return deciles (0.0 … 1.0) using `Series.quantile`.
- `build_carts(taFengFull) -> pd.DataFrame`  
  Group by `['customer_id','transaction_time']` and compute:
  - `num_items = sum(amount)`
  - `num_unique = count of rows (use .count() on 'amount')`
  - `total = sum(sales_price)`
- `unique_customers_per_day(taFengFull) -> pd.Series`  
  Number of unique customers each day.
- `add_day_of_week_and_week(df) -> pd.DataFrame`  
  Add ordered categorical `day_of_week` and integer `week_of_year` (ISO week).
- `count_by_weekday(df) -> pd.DataFrame`  
  Deduplicate (`week_of_year`, `day_of_week`, `customer_id`, `transaction_time`), then count by `['day_of_week','week_of_year']`.
