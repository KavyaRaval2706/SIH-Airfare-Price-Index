import pandas as pd
import numpy as np
from pathlib import Path

# ----------------------------------------------------
# 1. LOAD DATA
# ----------------------------------------------------
csv_file = Path(__file__).with_name("airfare_observations.csv")
fares = pd.read_csv(csv_file)

# Convert text columns into correct date/number formats.
fares["observation_date"] = pd.to_datetime(fares["observation_date"])
fares["travel_date"] = pd.to_datetime(fares["travel_date"])
fares["total_fare"] = pd.to_numeric(fares["total_fare"], errors="coerce")
fares["booking_window"] = pd.to_numeric(
    fares["booking_window"],
    errors="coerce"
)

fares = fares.dropna(
    subset=[
        "observation_date",
        "travel_date",
        "booking_window",
        "total_fare",
        "origin",
        "destination"
    ]
)

# ----------------------------------------------------
# 2. CLEAN AND STANDARDIZE THE PRODUCT
# We compare only like-for-like fares:
# observed + Economy + non-stop + valid total fare.
# ----------------------------------------------------
fares = fares[
    (fares["data_status"] == "Observed") &
    (fares["fare_type"] == "Economy") &
    (fares["stops"] == 0) &
    (fares["total_fare"] > 500) &
    (fares["total_fare"] < 100000)
].copy()

# Make route names such as DEL-BOM.
fares["route"] = fares["origin"] + "-" + fares["destination"]

# Put booking windows into meaningful groups.
def booking_window_band(days):
    if days <= 3:
        return "T+1 to T+3"
    elif days <= 7:
        return "T+4 to T+7"
    elif days <= 21:
        return "T+8 to T+21"
    elif days <= 45:
        return "T+22 to T+45"
    else:
        return "T+46 to T+60"

fares["window_band"] = fares["booking_window"].apply(
    booking_window_band
)

# ----------------------------------------------------
# 3. CALCULATE MEDIAN FARE FOR EACH DAILY MARKET CELL
# A cell = one date + one route + one booking-window band.
# Median protects the index from extreme fares.
# ----------------------------------------------------
daily_cells = (
    fares.groupby(
        ["observation_date", "route", "window_band"],
        as_index=False
    )
    .agg(
        current_fare=("total_fare", "median"),
        quote_count=("total_fare", "size")
    )
)

# ----------------------------------------------------
# 4. CHOOSE BASE PERIOD
# The median fare from 1-7 August becomes the reference.
# Base-period index is approximately 100.
# ----------------------------------------------------
base_start = pd.Timestamp("2026-08-01")
base_end = pd.Timestamp("2026-08-07")

base_cells = daily_cells[
    daily_cells["observation_date"].between(base_start, base_end)
]

base_prices = (
    base_cells.groupby(
        ["route", "window_band"],
        as_index=False
    )
    .agg(base_fare=("current_fare", "median"))
)

# Match each current cell with its base-period fare.
index_data = daily_cells.merge(
    base_prices,
    on=["route", "window_band"],
    how="inner"
)

# ----------------------------------------------------
# 5. CALCULATE PRICE RELATIVES
# Example: current ₹4,800 / base ₹4,000 × 100 = 120
# ----------------------------------------------------
index_data["price_relative"] = (
    index_data["current_fare"]
    / index_data["base_fare"]
    * 100
)

# ----------------------------------------------------
# 6. ASSIGN WEIGHTS
# For now all routes receive equal importance.
# Later, replace route weights with passenger-volume weights.
# ----------------------------------------------------
route_weights = {
    route: 1.0
    for route in index_data["route"].unique()
}

window_weights = {
    "T+1 to T+3": 0.10,
    "T+4 to T+7": 0.15,
    "T+8 to T+21": 0.35,
    "T+22 to T+45": 0.30,
    "T+46 to T+60": 0.10
}

index_data["route_weight"] = index_data["route"].map(route_weights)
index_data["window_weight"] = index_data["window_band"].map(window_weights)

index_data["final_weight"] = (
    index_data["route_weight"]
    * index_data["window_weight"]
)

# ----------------------------------------------------
# 7. DAILY AIRFARE INDEX
# ----------------------------------------------------
def weighted_average(group):
    return np.average(
        group["price_relative"],
        weights=group["final_weight"]
    )

daily_index = (
    index_data.groupby("observation_date")
    .apply(weighted_average)
    .reset_index(name="airfare_index")
)

# Show how much of the base market basket was available each day.
total_base_cells = len(base_prices)

daily_coverage = (
    index_data.groupby("observation_date")
    .size()
    .reset_index(name="available_cells")
)

daily_index = daily_index.merge(
    daily_coverage,
    on="observation_date",
    how="left"
)

daily_index["coverage_percent"] = (
    daily_index["available_cells"]
    / total_base_cells
    * 100
)

daily_index["quality_status"] = np.where(
    daily_index["coverage_percent"] >= 70,
    "Good coverage",
    "Low coverage"
)

# ----------------------------------------------------
# 8. WEEKLY AND MONTHLY INDICES
# ----------------------------------------------------
daily_index["week"] = (
    daily_index["observation_date"]
    .dt.to_period("W")
    .astype(str)
)

weekly_index = (
    daily_index.groupby("week", as_index=False)
    .agg(airfare_index=("airfare_index", "mean"))
)

weekly_index["week_on_week_change_percent"] = (
    weekly_index["airfare_index"]
    .pct_change()
    * 100
)

daily_index["month"] = (
    daily_index["observation_date"]
    .dt.to_period("M")
    .astype(str)
)

monthly_index = (
    daily_index.groupby("month", as_index=False)
    .agg(airfare_index=("airfare_index", "mean"))
)

monthly_index["month_on_month_change_percent"] = (
    monthly_index["airfare_index"]
    .pct_change()
    * 100
)

# ----------------------------------------------------
# 9. ROUTE-WISE INDEX
# ----------------------------------------------------
route_index = (
    index_data.groupby(["observation_date", "route"])
    .apply(weighted_average)
    .reset_index(name="route_airfare_index")
)

# ----------------------------------------------------
# 10. SAVE RESULTS
# ----------------------------------------------------
daily_index.to_csv("daily_airfare_index.csv", index=False)
weekly_index.to_csv("weekly_airfare_index.csv", index=False)
monthly_index.to_csv("monthly_airfare_index.csv", index=False)
route_index.to_csv("route_wise_airfare_index.csv", index=False)

print("\nSUCCESS: Index files created.")

print("\nDaily Airfare Index:")
print(daily_index[
    [
        "observation_date",
        "airfare_index",
        "coverage_percent",
        "quality_status"
    ]
].to_string(index=False))

print("\nWeekly Airfare Index:")
print(weekly_index.to_string(index=False))

print("\nMonthly Airfare Index:")
print(monthly_index.to_string(index=False))

import matplotlib.pyplot as plt

plt.figure(figsize=(12, 6))

plt.plot(
    daily_index["observation_date"],
    daily_index["airfare_index"],
    marker="o",
    color="blue",
    linewidth=2
)

plt.axhline(
    y=100,
    color="red",
    linestyle="--",
    label="Base Index = 100"
)

plt.title("Daily Airfare Price Index for India")
plt.xlabel("Observation Date")
plt.ylabel("Airfare Index")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()

plt.savefig("daily_airfare_index_chart.png", dpi=300)
plt.show()

# Route-wise average index chart
route_summary = (
    route_index.groupby("route", as_index=False)
    .agg(average_route_index=("route_airfare_index", "mean"))
    .sort_values("average_route_index", ascending=False)
)

plt.figure(figsize=(10, 6))

plt.bar(
    route_summary["route"],
    route_summary["average_route_index"],
    color="skyblue"
)

plt.axhline(
    y=100,
    color="red",
    linestyle="--",
    label="Base Index = 100"
)

plt.title("Route-wise Average Airfare Index")
plt.xlabel("Route")
plt.ylabel("Average Airfare Index")
plt.xticks(rotation=45)
plt.legend()
plt.tight_layout()

plt.savefig("route_wise_airfare_index_chart.png", dpi=300)
plt.show()

# Actual fare by booking-window chart
booking_fare_summary = (
    fares.groupby("window_band", as_index=False)
    .agg(median_total_fare=("total_fare", "median"))
)

window_order = [
    "T+1 to T+3",
    "T+4 to T+7",
    "T+8 to T+21",
    "T+22 to T+45",
    "T+46 to T+60"
]

booking_fare_summary["window_band"] = pd.Categorical(
    booking_fare_summary["window_band"],
    categories=window_order,
    ordered=True
)

booking_fare_summary = booking_fare_summary.sort_values("window_band")

plt.figure(figsize=(10, 6))

plt.bar(
    booking_fare_summary["window_band"],
    booking_fare_summary["median_total_fare"],
    color="orange"
)

plt.title("Median Airfare by Advance Booking Window")
plt.xlabel("Advance Booking Window")
plt.ylabel("Median Total Fare (INR)")
plt.xticks(rotation=20)
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()

plt.savefig("booking_window_actual_fares_chart.png", dpi=300)
plt.show()

# Airline-wise median fare chart
airline_summary = (
    fares.groupby("airline", as_index=False)
    .agg(median_total_fare=("total_fare", "median"))
    .sort_values("median_total_fare", ascending=False)
)

plt.figure(figsize=(10, 6))

plt.bar(
    airline_summary["airline"],
    airline_summary["median_total_fare"],
    color="mediumseagreen"
)

plt.title("Median Economy Airfare by Airline")
plt.xlabel("Airline")
plt.ylabel("Median Total Fare (INR)")
plt.xticks(rotation=25)
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()

plt.savefig("airline_wise_fare_chart.png", dpi=300)
plt.show()