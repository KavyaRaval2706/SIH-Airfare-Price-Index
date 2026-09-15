import pandas as pd
import numpy as np
from pathlib import Path
import psycopg

# ----------------------------------------------------
# DATABASE CONNECTION
# ----------------------------------------------------
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "airfare_project",
    "user": "postgres",
    "password": "Arya@2008"      # ← CHANGE THIS
}

def get_connection():
    return psycopg.connect(**DB_CONFIG)

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
        JOIN airlines a ON fo.airline_id = a.airline_id
        JOIN routes r ON fo.route_id = r.route_id
        JOIN booking_windows bw ON fo.booking_window_id = bw.booking_window_id
        WHERE fo.cabin_class_id = 1
          AND fo.fare BETWEEN 500 AND 100000
          AND fo.travel_date IS NOT NULL
    """
    fares = pd.read_sql(query, conn)

print(f"Loaded {len(fares):,} Economy observations")

# ----------------------------------------------------
# CLEANING
# ----------------------------------------------------
fares["travel_date"] = pd.to_datetime(fares["travel_date"])
fares["fare"] = pd.to_numeric(fares["fare"])
fares = fares.dropna(subset=["travel_date", "fare"])

fares["route"] = fares["source_city"] + "-" + fares["destination_city"]

def get_window_band(days):
    if days <= 3: return "T+1 to T+3"
    elif days <= 7: return "T+4 to T+7"
    elif days <= 21: return "T+8 to T+21"
    elif days <= 45: return "T+22 to T+45"
    else: return "T+46 to T+60"

fares["window_band"] = fares["days_before_departure"].apply(get_window_band)

# ----------------------------------------------------
# DAILY MEDIAN FARE PER ROUTE
# ----------------------------------------------------
print("Calculating daily median fares...")

daily_route = (
    fares.groupby(["travel_date", "route_id", "route"], as_index=False)
    .agg(median_fare=("fare", "median"))
)

# ----------------------------------------------------
# BASE PERIOD
# ----------------------------------------------------
min_date = daily_route["travel_date"].min()
base_end = min_date + pd.Timedelta(days=6)

print(f"Base period: {min_date.date()} to {base_end.date()}")

base_fares = (
    daily_route[daily_route["travel_date"].between(min_date, base_end)]
    .groupby(["route_id", "route"], as_index=False)
    .agg(base_fare=("median_fare", "median"))
)

index_data = daily_route.merge(base_fares, on=["route_id", "route"], how="inner")
index_data["price_relative"] = (index_data["median_fare"] / index_data["base_fare"]) * 100

# ----------------------------------------------------
# 1. DAILY INDEX
# ----------------------------------------------------
print("Building Daily Index...")

daily_index = (
    index_data.groupby("travel_date")["price_relative"]
    .mean()
    .reset_index(name="index_value")
    .sort_values("travel_date")
)

daily_index["percentage_change"] = daily_index["index_value"].pct_change() * 100
daily_index["percentage_change"] = daily_index["percentage_change"].round(2)
daily_index["index_value"] = daily_index["index_value"].round(2)
daily_index = daily_index.rename(columns={"travel_date": "index_date"})

# ----------------------------------------------------
# 2. WEEKLY INDEX
# ----------------------------------------------------
print("Building Weekly Index...")

daily_index_temp = daily_index.copy()
daily_index_temp["week"] = daily_index_temp["index_date"].dt.to_period("W").astype(str)

weekly_index = (
    daily_index_temp.groupby("week", as_index=False)
    .agg(index_value=("index_value", "mean"))
)

weekly_index["percentage_change"] = weekly_index["index_value"].pct_change() * 100
weekly_index["percentage_change"] = weekly_index["percentage_change"].round(2)
weekly_index["index_value"] = weekly_index["index_value"].round(2)
weekly_index = weekly_index.rename(columns={"week": "index_week"})

# ----------------------------------------------------
# 3. MONTHLY INDEX
# ----------------------------------------------------
print("Building Monthly Index...")

daily_index_temp["month"] = daily_index_temp["index_date"].dt.to_period("M").astype(str)

monthly_index = (
    daily_index_temp.groupby("month", as_index=False)
    .agg(index_value=("index_value", "mean"))
)

monthly_index["percentage_change"] = monthly_index["index_value"].pct_change() * 100
monthly_index["percentage_change"] = monthly_index["percentage_change"].round(2)
monthly_index["index_value"] = monthly_index["index_value"].round(2)
monthly_index = monthly_index.rename(columns={"month": "index_month"})

# ----------------------------------------------------
# 4. ROUTE-WISE INDEX
# ----------------------------------------------------
print("Building Route-wise Index...")

route_index = index_data[["travel_date", "route_id", "route", "price_relative"]].copy()
route_index[["source_city", "destination_city"]] = route_index["route"].str.split("-", n=1, expand=True)
route_index = route_index.rename(columns={
    "travel_date": "index_date",
    "price_relative": "index_value"
})
route_index = route_index.sort_values(["route_id", "index_date"])
route_index["percentage_change"] = route_index.groupby("route_id")["index_value"].pct_change() * 100
route_index["percentage_change"] = route_index["percentage_change"].round(2)
route_index["index_value"] = route_index["index_value"].round(2)
route_index = route_index[["index_date", "route_id", "source_city", "destination_city", "index_value", "percentage_change"]]

# ----------------------------------------------------
# 5. AIRLINE-WISE INDEX
# ----------------------------------------------------
print("Building Airline-wise Index...")

airline_daily = (
    fares.groupby(["travel_date", "airline_id", "airline_name"], as_index=False)
    .agg(median_fare=("fare", "median"))
)

airline_base = (
    airline_daily[airline_daily["travel_date"].between(min_date, base_end)]
    .groupby(["airline_id", "airline_name"], as_index=False)
    .agg(base_fare=("median_fare", "median"))
)

airline_data = airline_daily.merge(airline_base, on=["airline_id", "airline_name"], how="inner")
airline_data["index_value"] = (airline_data["median_fare"] / airline_data["base_fare"]) * 100

airline_index = airline_data[["travel_date", "airline_id", "airline_name", "index_value"]].copy()
airline_index = airline_index.rename(columns={"travel_date": "index_date"})
airline_index = airline_index.sort_values(["airline_id", "index_date"])
airline_index["percentage_change"] = airline_index.groupby("airline_id")["index_value"].pct_change() * 100
airline_index["percentage_change"] = airline_index["percentage_change"].round(2)
airline_index["index_value"] = airline_index["index_value"].round(2)

# ----------------------------------------------------
# 6. BOOKING WINDOW INDEX
# ----------------------------------------------------
print("Building Booking Window Index...")

window_daily = (
    fares.groupby(["travel_date", "window_band"], as_index=False)
    .agg(median_fare=("fare", "median"))
)

window_base = (
    window_daily[window_daily["travel_date"].between(min_date, base_end)]
    .groupby("window_band", as_index=False)
    .agg(base_fare=("median_fare", "median"))
)

window_data = window_daily.merge(window_base, on="window_band", how="inner")
window_data["index_value"] = (window_data["median_fare"] / window_data["base_fare"]) * 100

window_index = window_data[["travel_date", "window_band", "index_value"]].copy()
window_index = window_index.rename(columns={
    "travel_date": "index_date",
    "window_band": "booking_window"
})
window_index = window_index.sort_values(["booking_window", "index_date"])
window_index["percentage_change"] = window_index.groupby("booking_window")["index_value"].pct_change() * 100
window_index["percentage_change"] = window_index["percentage_change"].round(2)
window_index["index_value"] = window_index["index_value"].round(2)

# ----------------------------------------------------
# 7. CONTRIBUTIONS
# ----------------------------------------------------
print("Building Contributions...")

route_contrib = route_index.copy()
route_contrib["dimension_type"] = "route"
route_contrib["dimension_value"] = route_contrib["source_city"] + "-" + route_contrib["destination_city"]
route_contrib["contribution"] = route_contrib["index_value"]
route_contrib = route_contrib[["index_date", "dimension_type", "dimension_value", "contribution"]]

airline_contrib = airline_index.copy()
airline_contrib["dimension_type"] = "airline"
airline_contrib["dimension_value"] = airline_contrib["airline_name"]
airline_contrib["contribution"] = airline_contrib["index_value"]
airline_contrib = airline_contrib[["index_date", "dimension_type", "dimension_value", "contribution"]]

window_contrib = window_index.copy()
window_contrib["dimension_type"] = "booking_window"
window_contrib["dimension_value"] = window_contrib["booking_window"]
window_contrib["contribution"] = window_contrib["index_value"]
window_contrib = window_contrib[["index_date", "dimension_type", "dimension_value", "contribution"]]

contributions = pd.concat([route_contrib, airline_contrib, window_contrib], ignore_index=True)
contributions["contribution"] = contributions["contribution"].round(2)

# ----------------------------------------------------
# SAVE ALL FILES
# ----------------------------------------------------
out = Path(__file__).parent

daily_index.to_csv(out / "daily_airfare_index.csv", index=False)
weekly_index.to_csv(out / "weekly_airfare_index.csv", index=False)
monthly_index.to_csv(out / "monthly_airfare_index.csv", index=False)
route_index.to_csv(out / "route_wise_airfare_index.csv", index=False)
airline_index.to_csv(out / "airline_wise_airfare_index.csv", index=False)
window_index.to_csv(out / "booking_window_index.csv", index=False)
contributions.to_csv(out / "index_contributions.csv", index=False)

print("\n" + "="*65)
print("SUCCESS! All files created:")
print("  • daily_airfare_index.csv")
print("  • weekly_airfare_index.csv")
print("  • monthly_airfare_index.csv")
print("  • route_wise_airfare_index.csv")
print("  • airline_wise_airfare_index.csv")
print("  • booking_window_index.csv")
print("  • index_contributions.csv")
print("="*65)

print("\nDaily Index (first 8 rows):")
print(daily_index.head(8).to_string(index=False))

print("\nWeekly Index:")
print(weekly_index.to_string(index=False))

print("\nMonthly Index:")
print(monthly_index.to_string(index=False))