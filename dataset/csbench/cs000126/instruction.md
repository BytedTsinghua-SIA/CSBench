# Lab 2 — Data Wrangling with Pandas (Student Skeleton + Tests)

## What you will do
Implement core data-wrangling utilities in `lab02.py` and validate them with `pytest` using `test_lab02.py`. The tasks mirror the original notebook but in a clean, testable Python module without okpy.

## Files
- `lab02.py`: Fill in all `TODO`s. Functions must be vectorized where natural and should not modify inputs in place.
- `test_lab02.py`: A comprehensive test suite with reference implementations and synthetic fixtures. It also contains **optional** tests that read external files (`flights.dat`, `airports.dat`) if present.

## Functions to implement
1. `extract_hour(time)`: Integer hour from military time.
2. `extract_mins(time)`: Integer minutes from military time.
3. `convert_to_minofday(time)`: Minutes since 00:00.
4. `calc_time_diff(x_sched, y_actual)`: Delay minutes.
5. `filter_delayed15(flights, ...)`: Rows with departure delay > 15.
6. `delayed_dest_cities(delayed_flights, airports, ...)`: Alphabetically sorted destination city names for delayed flights.
7. `top10_tailnums_by_unique_destinations(flights, ...)`: Top 10 tail numbers by unique destination count.
8. `add_sfo_arr_delay_avg(airports, flights, ...)`: Merge average SFO-origin departure delay by destination as `sfo_arr_delay_avg`.
