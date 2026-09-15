import pandas as pd

# Load cleaned Dataset 2
df = pd.read_csv(
    "C:\\Users\\Kavya\\DeviantX\\SIH-Airfare-Price-Index\\Data\\processed\\airfare_clean_2.csv"
)

print("Dataset shape:", df.shape)


# 1. Check required columns
required_columns = [
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


# 2. Check missing values
print("\nMissing values:")
print(df.isna().sum())


# 3. Check booking window
print("\nInvalid booking windows:")
print((df["booking_window"] < 1).sum())


# 4. Check fare
print("\nInvalid fares:")
print((df["fare"] <= 0).sum())


# 5. Check duration
print("\nInvalid durations:")
print((df["duration_minutes"] <= 0).sum())


# 6. Check stops
print("\nInvalid stops:")
print((~df["stops"].isin([0, 1, 2])).sum())


# 7. Check source and destination
print("\nSame source and destination:")
print((df["source"] == df["destination"]).sum())


# 8. Check duplicate rows
print("\nDuplicate rows:")
print(df.duplicated().sum())


# 9. Check airline values
print("\nUnique airlines:")
print(df["airline"].unique())


# 10. Check cabin classes
print("\nUnique cabin classes:")
print(df["cabin_class"].unique())


# 11. Check data types
print("\nData types:")
print(df.dtypes)