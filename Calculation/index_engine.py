import os
from pathlib import Path

import pandas as pd
import numpy as np
import psycopg
from dotenv import load_dotenv


# ============================================================
# 1. DATABASE CONFIGURATION
# ============================================================

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}


def get_connection():
    return psycopg.connect(**DB_CONFIG)


# ============================================================
# 2. LOAD DATA FROM POSTGRESQL
# ============================================================

print("Connecting to PostgreSQL...")

with get_connection() as conn:

    query = """
        SELECT
            fo.airline_id,
            a.airline_name,
            fo.route_id,
            r.source_city,
            r.destination_city,
            fo.booking_window_id,
            bw.days_before_departure,
            fo.travel_date,
            fo.fare
        FROM fare_observations fo

        JOIN airlines a
            ON fo.airline_id = a.airline_id

        JOIN routes r
            ON fo.route_id = r.route_id

        JOIN booking_windows bw
            ON fo.booking_window_id = bw.booking_window_id

        JOIN cabin_classes cc
            ON fo.cabin_class_id = cc.cabin_class_id

        WHERE cc.class_name = 'Economy'
          AND fo.fare BETWEEN 500 AND 100000
          AND fo.travel_date IS NOT NULL
          AND bw.days_before_departure BETWEEN 1 AND 50
    """

    fares = pd.read_sql(query, conn)


print(f"Loaded {len(fares):,} Economy observations")


# ============================================================
# 3. CLEAN DATA USED FOR CALCULATION
# ============================================================

print("Cleaning data...")

fares["travel_date"] = pd.to_datetime(
    fares["travel_date"],
    errors="coerce"
)

fares["fare"] = pd.to_numeric(
    fares["fare"],
    errors="coerce"
)

fares["days_before_departure"] = pd.to_numeric(
    fares["days_before_departure"],
    errors="coerce"
)

fares = fares.dropna(
    subset=[
        "travel_date",
        "fare",
        "days_before_departure"
    ]
)

fares = fares[
    fares["days_before_departure"].between(1, 50)
]

fares["days_before_departure"] = (
    fares["days_before_departure"].astype(int)
)

fares["route"] = (
    fares["source_city"]
    + "-"
    + fares["destination_city"]
)


# ============================================================
# 4. DAILY ROUTE MEDIAN FARES
# ============================================================

print("Calculating daily median fares...")

daily_route = (
    fares
    .groupby(
        [
            "travel_date",
            "route_id",
            "route"
        ],
        as_index=False
    )
    .agg(
        median_fare=("fare", "median")
    )
)


# ============================================================
# 5. BASE PERIOD
# ============================================================

min_date = daily_route["travel_date"].min()

base_end = (
    min_date
    + pd.Timedelta(days=6)
)

print(
    f"Base period: "
    f"{min_date.date()} to {base_end.date()}"
)


# ============================================================
# 6. ROUTE BASE FARES
# ============================================================

base_fares = (
    daily_route[
        daily_route["travel_date"].between(
            min_date,
            base_end
        )
    ]
    .groupby(
        [
            "route_id",
            "route"
        ],
        as_index=False
    )
    .agg(
        base_fare=("median_fare", "median")
    )
)


# ============================================================
# 7. DAILY OVERALL INDEX
# ============================================================

print("Building Daily Index...")

index_data = daily_route.merge(
    base_fares,
    on=[
        "route_id",
        "route"
    ],
    how="inner"
)

index_data["price_relative"] = (
    index_data["median_fare"]
    / index_data["base_fare"]
) * 100


daily_index = (
    index_data
    .groupby(
        "travel_date"
    )["price_relative"]
    .mean()
    .reset_index(
        name="index_value"
    )
    .sort_values("travel_date")
)

daily_index["percentage_change"] = (
    daily_index["index_value"].pct_change()
    * 100
)

daily_index["index_value"] = (
    daily_index["index_value"].round(2)
)

daily_index["percentage_change"] = (
    daily_index["percentage_change"].round(2)
)

daily_index = daily_index.rename(
    columns={
        "travel_date": "index_date"
    }
)


# ============================================================
# 8. WEEKLY INDEX
# ============================================================

print("Building Weekly Index...")

daily_index_temp = daily_index.copy()

daily_index_temp["week"] = (
    daily_index_temp["index_date"]
    .dt.to_period("W")
    .astype(str)
)

weekly_index = (
    daily_index_temp
    .groupby("week", as_index=False)
    .agg(
        index_value=("index_value", "mean")
    )
)

weekly_index["percentage_change"] = (
    weekly_index["index_value"].pct_change()
    * 100
)

weekly_index["index_value"] = (
    weekly_index["index_value"].round(2)
)

weekly_index["percentage_change"] = (
    weekly_index["percentage_change"].round(2)
)

weekly_index = weekly_index.rename(
    columns={
        "week": "index_week"
    }
)


# ============================================================
# 9. MONTHLY INDEX
# ============================================================

print("Building Monthly Index...")

daily_index_temp["month"] = (
    daily_index_temp["index_date"]
    .dt.to_period("M")
    .astype(str)
)

monthly_index = (
    daily_index_temp
    .groupby("month", as_index=False)
    .agg(
        index_value=("index_value", "mean")
    )
)

monthly_index["percentage_change"] = (
    monthly_index["index_value"].pct_change()
    * 100
)

monthly_index["index_value"] = (
    monthly_index["index_value"].round(2)
)

monthly_index["percentage_change"] = (
    monthly_index["percentage_change"].round(2)
)

monthly_index = monthly_index.rename(
    columns={
        "month": "index_month"
    }
)


# ============================================================
# 10. ROUTE-WISE INDEX
# ============================================================

print("Building Route-wise Index...")

route_index = index_data[
    [
        "travel_date",
        "route_id",
        "route",
        "price_relative"
    ]
].copy()

route_index[
    [
        "source_city",
        "destination_city"
    ]
] = route_index["route"].str.split(
    "-",
    n=1,
    expand=True
)

route_index = route_index.rename(
    columns={
        "travel_date": "index_date",
        "price_relative": "index_value"
    }
)

route_index = route_index.sort_values(
    [
        "route_id",
        "index_date"
    ]
)

route_index["percentage_change"] = (
    route_index
    .groupby("route_id")["index_value"]
    .pct_change()
    * 100
)

route_index["index_value"] = (
    route_index["index_value"].round(2)
)

route_index["percentage_change"] = (
    route_index["percentage_change"].round(2)
)

route_index = route_index[
    [
        "index_date",
        "route_id",
        "source_city",
        "destination_city",
        "index_value",
        "percentage_change"
    ]
]


# ============================================================
# 11. AIRLINE-WISE INDEX
# ============================================================

print("Building Airline-wise Index...")

airline_daily = (
    fares
    .groupby(
        [
            "travel_date",
            "airline_id",
            "airline_name"
        ],
        as_index=False
    )
    .agg(
        median_fare=("fare", "median")
    )
)

airline_base = (
    airline_daily[
        airline_daily["travel_date"].between(
            min_date,
            base_end
        )
    ]
    .groupby(
        [
            "airline_id",
            "airline_name"
        ],
        as_index=False
    )
    .agg(
        base_fare=("median_fare", "median")
    )
)

airline_data = airline_daily.merge(
    airline_base,
    on=[
        "airline_id",
        "airline_name"
    ],
    how="inner"
)

airline_data["index_value"] = (
    airline_data["median_fare"]
    / airline_data["base_fare"]
) * 100

airline_index = airline_data[
    [
        "travel_date",
        "airline_id",
        "airline_name",
        "index_value"
    ]
].copy()

airline_index = airline_index.rename(
    columns={
        "travel_date": "index_date"
    }
)

airline_index = airline_index.sort_values(
    [
        "airline_id",
        "index_date"
    ]
)

airline_index["percentage_change"] = (
    airline_index
    .groupby("airline_id")["index_value"]
    .pct_change()
    * 100
)

airline_index["index_value"] = (
    airline_index["index_value"].round(2)
)

airline_index["percentage_change"] = (
    airline_index["percentage_change"].round(2)
)


# ============================================================
# 12. BOOKING-WINDOW INDEX
# ============================================================
#
# IMPORTANT:
# Every booking window is kept separately.
#
# T+1
# T+2
# T+3
# ...
# T+50
#
# There are NO booking-window bands.
#
# The index compares each booking window's median fare
# against the T+1 median fare.
# ============================================================

print("Building Booking Window Index...")

booking_window_daily = (
    fares
    .groupby(
        [
            "travel_date",
            "days_before_departure"
        ],
        as_index=False
    )
    .agg(
        median_fare=("fare", "median")
    )
)

booking_window_median = (
    booking_window_daily
    .groupby(
        "days_before_departure",
        as_index=False
    )
    .agg(
        median_fare=("median_fare", "median")
    )
)

# ------------------------------------------------------------
# T+1 is the reference booking window.
# ------------------------------------------------------------

t1_rows = booking_window_median[
    booking_window_median["days_before_departure"] == 1
]

if t1_rows.empty:
    raise ValueError(
        "T+1 booking window does not exist in the data."
    )

t1_base_fare = (
    t1_rows["median_fare"].iloc[0]
)

# ------------------------------------------------------------
# Calculate index for EVERY individual booking window.
# ------------------------------------------------------------

booking_window_index = booking_window_median.copy()

booking_window_index["index_value"] = (
    booking_window_index["median_fare"]
    / t1_base_fare
) * 100

# ------------------------------------------------------------
# Sort T+1, T+2, ..., T+50.
# ------------------------------------------------------------

booking_window_index = (
    booking_window_index
    .sort_values("days_before_departure")
)

# ------------------------------------------------------------
# Percentage change from previous booking window.
#
# Example:
# T+2 compared with T+1
# T+3 compared with T+2
# T+4 compared with T+3
# ------------------------------------------------------------

booking_window_index["percentage_change"] = (
    booking_window_index["index_value"]
    .pct_change()
    * 100
)

booking_window_index = booking_window_index.rename(
    columns={
        "days_before_departure": "booking_window"
    }
)

booking_window_index["index_value"] = (
    booking_window_index["index_value"].round(2)
)

booking_window_index["percentage_change"] = (
    booking_window_index["percentage_change"].round(2)
)

booking_window_index = booking_window_index[
    [
        "booking_window",
        "median_fare",
        "index_value",
        "percentage_change"
    ]
]

print(
    "Booking Window Index created for "
    f"{booking_window_index['booking_window'].nunique()} "
    "individual booking windows"
)


# ============================================================
# 13. CONTRIBUTIONS — WHY DID THE INDEX CHANGE?
# ============================================================

output_directory = (
    Path(__file__).parent
    / "Output"
)


print("\nBuilding Contributions...")

# ------------------------------------------------------------
# 13A. ROUTE CONTRIBUTIONS
# ------------------------------------------------------------

# Use the EXACT route price relatives used to build daily_index.
route_values = index_data[
    ["travel_date", "route_id", "route", "price_relative"]
].copy()

route_values["travel_date"] = pd.to_datetime(
    route_values["travel_date"]
)

# Daily overall index BEFORE rounding
daily_index_raw = (
    index_data
    .groupby("travel_date")["price_relative"]
    .mean()
    .sort_index()
)

# Previous day's overall index
previous_daily_index = daily_index_raw.shift(1)

# For every current-day route:
#
# contribution =
# (route price relative - previous overall index)
# ------------------------------------------------
#             number of routes today
#
# The sum of all route contributions therefore equals:
#
# current daily index - previous daily index

route_values["previous_daily_index"] = (
    route_values["travel_date"].map(previous_daily_index)
)

route_values["route_count"] = (
    route_values
    .groupby("travel_date")["route_id"]
    .transform("count")
)

route_values["contribution"] = (
    (
        route_values["price_relative"]
        - route_values["previous_daily_index"]
    )
    / route_values["route_count"]
)

# First date has no previous index
route_values = route_values.dropna(
    subset=["previous_daily_index"]
)

route_output = route_values[
    [
        "travel_date",
        "route_id",
        "route",
        "contribution"
    ]
].copy()

route_output["dimension_type"] = "route"

route_output = route_output.rename(
    columns={
        "travel_date": "index_date"
    }
)


# ------------------------------------------------------------
# 13B. VERIFY ROUTE CONTRIBUTIONS
# ------------------------------------------------------------

actual_route_change = (
    route_output
    .groupby("index_date")["contribution"]
    .sum()
)

expected_route_change = daily_index_raw.diff()

comparison = pd.DataFrame({
    "expected": expected_route_change,
    "actual": actual_route_change
}).dropna()

max_difference = (
    comparison["expected"] - comparison["actual"]
).abs().max()


print(
    f"Maximum route contribution reconciliation difference: "
    f"{max_difference:.12f}"
)

if max_difference > 1e-10:
    raise ValueError(
        "Route contributions do not reconcile with the "
        f"daily index change. Maximum difference: "
        f"{max_difference}"
    )

print("Route contribution reconciliation PASSED.")


# ------------------------------------------------------------
# 13C. AIRLINE CONTRIBUTIONS
# ------------------------------------------------------------

# Keep airline contributions as a SEPARATE analytical breakdown.
# They explain movement in the airline-wise index, not the
# overall route-based daily index.

airline_values = airline_data[
    [
        "travel_date",
        "airline_id",
        "airline_name",
        "index_value"
    ]
].copy()

airline_values["travel_date"] = pd.to_datetime(
    airline_values["travel_date"]
)

airline_daily_index = (
    airline_values
    .groupby("travel_date")["index_value"]
    .mean()
    .sort_index()
)

previous_airline_index = airline_daily_index.shift(1)

airline_values["previous_daily_index"] = (
    airline_values["travel_date"].map(previous_airline_index)
)

airline_values["airline_count"] = (
    airline_values
    .groupby("travel_date")["airline_id"]
    .transform("count")
)

airline_values["contribution"] = (
    (
        airline_values["index_value"]
        - airline_values["previous_daily_index"]
    )
    / airline_values["airline_count"]
)

airline_values = airline_values.dropna(
    subset=["previous_daily_index"]
)

airline_output = airline_values[
    [
        "travel_date",
        "airline_id",
        "airline_name",
        "contribution"
    ]
].copy()

airline_output["dimension_type"] = "airline"

airline_output = airline_output.rename(
    columns={
        "travel_date": "index_date",
    }
)


# ------------------------------------------------------------
# 13D. COMBINE ROUTE + AIRLINE CONTRIBUTIONS
# ------------------------------------------------------------

contribution_output = pd.concat(
    [
        route_output,
        airline_output
    ],
    ignore_index=True
)

contribution_output["contribution"] = (
    contribution_output["contribution"].round(4)
)

contribution_output = contribution_output[
    [
        "index_date",
        "dimension_type",
        "route",
        "contribution"
    ]
].rename(
    columns={
        "route": "dimension_value"
    }
).sort_values(
    [
        "index_date",
        "dimension_type",
        "contribution"
    ],
    ascending=[
        True,
        True,
        False
    ]
)

contribution_output.to_csv(
    output_directory / "index_contributions.csv",
    index=False
)

print(
    f"Saved: "
    f"{output_directory / 'index_contributions.csv'}"
)

print(
    f"Contribution rows: {len(contribution_output)}"
)


# ============================================================
# 14. SAVE OUTPUT FILES
# ============================================================



daily_index.to_csv(
    output_directory / "daily_airfare_index.csv",
    index=False
)

weekly_index.to_csv(
    output_directory / "weekly_airfare_index.csv",
    index=False
)

monthly_index.to_csv(
    output_directory / "monthly_airfare_index.csv",
    index=False
)

route_index.to_csv(
    output_directory / "route_wise_airfare_index.csv",
    index=False
)

airline_index.to_csv(
    output_directory / "airline_wise_airfare_index.csv",
    index=False
)

booking_window_index.to_csv(
    output_directory / "booking_window_index.csv",
    index=False
)

contribution_output.to_csv(
    output_directory / "index_contributions.csv",
    index=False
)


# ============================================================
# 15. FINAL SUMMARY
# ============================================================

print()
print("=" * 65)
print("SUCCESS! All files created:")
print(
    f"  • daily_airfare_index.csv "
    f"({len(daily_index):,} rows)"
)

print(
    f"  • weekly_airfare_index.csv "
    f"({len(weekly_index):,} rows)"
)

print(
    f"  • monthly_airfare_index.csv "
    f"({len(monthly_index):,} rows)"
)

print(
    f"  • route_wise_airfare_index.csv "
    f"({len(route_index):,} rows)"
)

print(
    f"  • airline_wise_airfare_index.csv "
    f"({len(airline_index):,} rows)"
)

print(
    f"  • booking_window_index.csv "
    f"({len(booking_window_index):,} rows)"
)

print(
    f"  • index_contributions.csv "
    f"({len(contribution_output):,} rows)"
)

print("=" * 65)


# ============================================================
# 16. PREVIEW
# ============================================================

print()
print("Daily Index (first 8 rows):")

print(
    daily_index.head(8).to_string(
        index=False
    )
)


print()
print("Weekly Index:")

print(
    weekly_index.to_string(
        index=False
    )
)


print()
print("Monthly Index:")

print(
    monthly_index.to_string(
        index=False
    )
)


print()
print("Booking Window Index:")

print(
    booking_window_index.to_string(
        index=False
    )
)


print()
print("Contribution Preview:")

print(
    contribution_output.head(20).to_string(
        index=False
    )
)