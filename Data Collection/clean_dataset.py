import pandas as pd

df = pd.read_csv("airfare_raw.csv")

original_rows = len(df)

print("Original rows:", original_rows)

print()
print("Cleaning started...")
print()

# 1. Remove duplicate observations
df = df.drop_duplicates(
    subset=["observation_id"],
    keep="first"
)

print("Duplicates removed")

# 2. Remove rows with missing important information
important_columns = [
    "observation_id",
    "observation_date",
    "travel_date",
    "airline",
    "origin",
    "destination",
    "base_fare",
    "taxes",
    "mandatory_charges",
    "total_fare"
]

df = df.dropna(
    subset=important_columns
)

print("Rows with missing important values removed")

# 3. Remove negative prices
df = df[
    (df["base_fare"] >= 0) &
    (df["taxes"] >= 0) &
    (df["mandatory_charges"] >= 0)
]

print("Invalid negative prices removed")

# 4. Convert dates
df["observation_date"] = pd.to_datetime(
    df["observation_date"],
    errors="coerce"
)

df["travel_date"] = pd.to_datetime(
    df["travel_date"],
    errors="coerce"
)

# 5. Remove rows with invalid dates
df = df.dropna(
    subset=["observation_date", "travel_date"]
)

print("Invalid dates removed")

# 6. Recalculate booking window
df["calculated_booking_window"] = (
    df["travel_date"] -
    df["observation_date"]
).dt.days

df = df[
    df["booking_window"] ==
    df["calculated_booking_window"]
]

print("Incorrect booking windows removed")

df.drop(
    columns=["calculated_booking_window"],
    inplace=True
)

# 7. Recalculate total fare
df["calculated_total_fare"] = (
    df["base_fare"] +
    df["taxes"] +
    df["mandatory_charges"]
)

df = df[
    df["total_fare"] ==
    df["calculated_total_fare"]
]

print("Incorrect total fares removed")

df.drop(
    columns=["calculated_total_fare"],
    inplace=True
)

# 8. Remove invalid routes
df = df[
    df["origin"] != df["destination"]
]

print("Invalid routes removed")

# Save cleaned dataset
df.to_csv(
    "airfare_clean.csv",
    index=False
)

print()
print("========== CLEANING REPORT ==========")
print()

print("Original rows:", original_rows)
print("Clean rows:", len(df))
print("Rows removed:", original_rows - len(df))

print()
print("Clean dataset saved as: airfare_clean.csv")