import pandas as pd

# Load final normalized dataset
df = pd.read_csv(
    "C:\\Users\\Kavya\\DeviantX\\SIH-Airfare-Price-Index\\Data\\processed\\fare_observations.csv",low_memory=False
)

print("Dataset shape:", df.shape)


# 1. Required columns
required_columns = [
    "observation_id",
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

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

print("\nMissing required columns:")
print(missing_columns)


# 2. Missing values
print("\nMissing values:")
print(df.isna().sum())


# 3. Observation ID uniqueness
print("\nDuplicate observation IDs:")
print(df["observation_id"].duplicated().sum())


# 4. Duplicate complete rows
print("\nDuplicate rows:")
print(df.duplicated().sum())


# 5. Source datasets
print("\nSource distribution:")
print(df["source_dataset"].value_counts())


# 6. Booking window
print("\nInvalid booking windows:")
print((df["booking_window"] < 1).sum())


# 7. Fare
print("\nInvalid fares:")
print((df["fare"] <= 0).sum())


# 8. Duration
print("\nInvalid durations:")
print((df["duration_minutes"] <= 0).sum())


# 9. Stops
print("\nInvalid stops:")
print((~df["stops"].isin([0, 1, 2])).sum())


# 10. Source and destination
print("\nSame source and destination:")
print((df["source"] == df["destination"]).sum())


# 11. Data types
print("\nData types:")
print(df.dtypes)