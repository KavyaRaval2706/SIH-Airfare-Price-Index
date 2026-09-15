import pandas as pd

df = pd.read_csv("C:\\Users\\Kavya\\DeviantX\\SIH-Airfare-Price-Index\\Data\\raw\\Scraped_dataset.csv")


# Dates
df["booking_date"] = pd.to_datetime(
    df["Date of Booking"],
    dayfirst=True,
    errors="coerce"
)

df["travel_date"] = pd.to_datetime(
    df["Date of Journey"],
    dayfirst=True,
    errors="coerce"
)

# Split Airline-Class
parts = df["Airline-Class"].str.split("\n", expand=True)

df["airline"] = parts[0].str.strip()
df["flight_code"] = parts[1].str.strip()
df["cabin_class"] = parts[2].str.strip()

# Clean stops
df["stops"] = (
    df["Total Stops"]
    .str.extract(r"(\d+)")[0]
    .astype("Int64")
)

df.loc[df["Total Stops"].str.contains("non-stop", case=False, na=False), "stops"] = 0

# Clean price
df["fare"] = (
    df["Price"]
    .str.replace(",", "", regex=False)
    .astype(float)
)

"""
print(df[
    [
        "booking_date",
        "travel_date",
        "airline",
        "flight_code",
        "cabin_class",
        "stops",
        "fare"
    ]
].head(10))
"""

# Extract departure time and source city
departure_parts = df["Departure Time"].str.split("\n", expand=True)

df["departure_time"] = departure_parts[0].str.strip()
df["source"] = departure_parts[1].str.strip()

# Extract arrival time and destination city
arrival_parts = df["Arrival Time"].str.split("\n", expand=True)

df["arrival_time"] = arrival_parts[0].str.strip()
df["destination"] = arrival_parts[1].str.strip()

# Convert duration to minutes
duration_parts = df["Duration"].str.extract(
    r"(?P<hours>\d+)h\s*(?P<minutes>\d+)m"
)

df["duration_minutes"] = (
    duration_parts["hours"].astype(int) * 60
    + duration_parts["minutes"].astype(int)
)

"""
print(df[
    [
        "source",
        "destination",
        "departure_time",
        "arrival_time",
        "duration_minutes"
    ]
].head(10))
"""

# Calculate booking window
df["booking_window"] = (
    df["travel_date"] - df["booking_date"]
).dt.days



"""
print("\nBOOKING WINDOW:")
print(df["booking_window"].describe())

print("\nBOOKING WINDOW VALUES:")
print(sorted(df["booking_window"].unique()))

print("\nTARGET WINDOWS:")
print(
    df[df["booking_window"].isin([1, 7, 15, 21, 30, 45, 60])]
    ["booking_window"]
    .value_counts()
    .sort_index()
)
"""

# Normalize text values
df["airline"] = df["airline"].str.strip()
df["flight_code"] = df["flight_code"].str.replace(r"\s+", "", regex=True)
df["cabin_class"] = df["cabin_class"].str.strip().str.upper()
df["source"] = df["source"].str.strip()
df["destination"] = df["destination"].str.strip()
df["departure_time"] = df["departure_time"].str.strip()
df["arrival_time"] = df["arrival_time"].str.strip()

# Remove exact duplicate observations
df = df.drop_duplicates()

# Keep only required columns
final_columns = [
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

df = df[final_columns]

# Save cleaned dataset
df.to_csv(
    "C:\\Users\\Kavya\\DeviantX\\SIH-Airfare-Price-Index\\Data\\processed\\airfare_clean.csv",
    index=False
)

print("\nCleaning completed.")
print("Final shape:", df.shape)
print("Cleaned file saved successfully.")