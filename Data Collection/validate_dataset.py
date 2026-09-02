import pandas as pd

df = pd.read_csv("airfare_raw.csv")

errors = []

required_columns = [
    "observation_id",
    "observation_date",
    "source",
    "airline",
    "flight_number",
    "origin",
    "destination",
    "travel_date",
    "departure_time",
    "stops",
    "booking_window",
    "fare_type",
    "base_fare",
    "taxes",
    "mandatory_charges",
    "total_fare",
    "data_status"
]

for column in required_columns:
    if column not in df.columns:
        errors.append(f"Missing column: {column}")

for index, row in df.iterrows():

    observation_id = row["observation_id"]

    if pd.isna(row["airline"]):
        errors.append(
            f"{observation_id}: Missing airline"
        )

    if pd.isna(row["base_fare"]):
        errors.append(
            f"{observation_id}: Missing base fare"
        )

    if pd.isna(row["taxes"]):
        errors.append(
            f"{observation_id}: Missing taxes"
        )

    if pd.isna(row["mandatory_charges"]):
        errors.append(
            f"{observation_id}: Missing mandatory charges"
        )

    if pd.isna(row["total_fare"]):
        errors.append(
            f"{observation_id}: Missing total fare"
        )

    if not pd.isna(row["base_fare"]) and row["base_fare"] < 0:
        errors.append(
            f"{observation_id}: Negative base fare"
        )

    if not pd.isna(row["taxes"]) and row["taxes"] < 0:
        errors.append(
            f"{observation_id}: Negative taxes"
        )

    if not pd.isna(row["mandatory_charges"]) and row["mandatory_charges"] < 0:
        errors.append(
            f"{observation_id}: Negative mandatory charges"
        )

    if (
        not pd.isna(row["base_fare"])
        and not pd.isna(row["taxes"])
        and not pd.isna(row["mandatory_charges"])
        and not pd.isna(row["total_fare"])
    ):
        calculated_total = (
            row["base_fare"]
            + row["taxes"]
            + row["mandatory_charges"]
        )

        if calculated_total != row["total_fare"]:
            errors.append(
                f"{observation_id}: Incorrect total fare"
            )

    observation_date = pd.to_datetime(
        row["observation_date"],
        errors="coerce"
    )

    travel_date = pd.to_datetime(
        row["travel_date"],
        errors="coerce"
    )

    if pd.isna(observation_date):
        errors.append(
            f"{observation_id}: Invalid observation date"
        )

    if pd.isna(travel_date):
        errors.append(
            f"{observation_id}: Invalid travel date"
        )

    if not pd.isna(observation_date) and not pd.isna(travel_date):

        calculated_window = (
            travel_date - observation_date
        ).days

        if calculated_window != row["booking_window"]:
            errors.append(
                f"{observation_id}: Incorrect booking window"
            )

    if row["origin"] == row["destination"]:
        errors.append(
            f"{observation_id}: Origin and destination are same"
        )

duplicate_count = df.duplicated(
    subset=["observation_id"]
).sum()

if duplicate_count > 0:
    errors.append(
        f"Duplicate observation IDs found: {duplicate_count}"
    )

print()
print("========== DATA VALIDATION REPORT ==========")
print()

if len(errors) == 0:
    print("No errors found!")
else:
    print("Total problems found:", len(errors))
    print()

    for error in errors:
        print("❌", error)

print()
print("============================================")