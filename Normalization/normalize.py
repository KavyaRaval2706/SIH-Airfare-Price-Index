import pandas as pd


# Load cleaned datasets
df1 = pd.read_csv(
    "C:\\Users\\Kavya\\DeviantX\\SIH-Airfare-Price-Index\\Data\\processed\\airfare_clean.csv"
)

df2 = pd.read_csv(
    "C:\\Users\\Kavya\\DeviantX\\SIH-Airfare-Price-Index\\Data\\processed\\airfare_clean_2.csv"
)


# --------------------------------------------------
# Normalize Dataset 1
# --------------------------------------------------

df1["source_dataset"] = "EaseMyTrip_Dataset_1"


# Standardize cabin class
df1["cabin_class"] = df1["cabin_class"].str.title()


# Standardize fare
df1["fare"] = pd.to_numeric(df1["fare"], errors="coerce")


# Standardize numeric columns
df1["booking_window"] = pd.to_numeric(
    df1["booking_window"],
    errors="coerce"
)

df1["duration_minutes"] = pd.to_numeric(
    df1["duration_minutes"],
    errors="coerce"
)

df1["stops"] = pd.to_numeric(
    df1["stops"],
    errors="coerce"
)


# --------------------------------------------------
# Normalize Dataset 2
# --------------------------------------------------

df2["source_dataset"] = "EaseMyTrip_Dataset_2"


# Standardize cabin class
df2["cabin_class"] = df2["cabin_class"].str.title()


# Standardize fare
df2["fare"] = pd.to_numeric(df2["fare"], errors="coerce")


# Standardize numeric columns
df2["booking_window"] = pd.to_numeric(
    df2["booking_window"],
    errors="coerce"
)

df2["duration_minutes"] = pd.to_numeric(
    df2["duration_minutes"],
    errors="coerce"
)

df2["stops"] = pd.to_numeric(
    df2["stops"],
    errors="coerce"
)


# --------------------------------------------------
# Common column order
# --------------------------------------------------

final_columns = [
    "source_dataset",
    "airline",
    "flight_code",
    "source",
    "destination",
    "booking_date",
    "travel_date",
    "booking_window",
    "cabin_class",
    "departure_time",
    "arrival_time",
    "duration_minutes",
    "stops",
    "fare"
]

df1 = df1[final_columns]
df2 = df2[final_columns]


# --------------------------------------------------
# Combine both datasets
# --------------------------------------------------

df = pd.concat(
    [df1, df2],
    ignore_index=True
)




# --------------------------------------------------
# Save normalized dataset
# --------------------------------------------------

df.to_csv(
    "C:\\Users\\Kavya\\DeviantX\\SIH-Airfare-Price-Index\\Data\\processed\\fare_observations.csv",
    index=False
)


print("\nNormalization completed.")
print("Dataset 1 rows:", len(df1))
print("Dataset 2 rows:", len(df2))
print("Combined rows:", len(df))
print("Columns:", len(df.columns))
print("\nSource distribution:")
print(df["source_dataset"].value_counts())
print("\nNormalized file saved successfully.")