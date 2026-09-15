import pandas as pd

# Load Dataset 2
df = pd.read_csv(
    "C:\\Users\\Kavya\\DeviantX\\SIH-Airfare-Price-Index\\Data\\raw\\Clean_Dataset_2.csv"
)

# Remove unnecessary index column
df = df.drop(columns=["Unnamed: 0"])


# Rename columns
df = df.rename(columns={
    "source_city": "source",
    "destination_city": "destination",
    "class": "cabin_class",
    "days_left": "booking_window"
})


# Normalize text
df["airline"] = df["airline"].str.strip()
df["flight"] = df["flight"].str.strip()
df["source"] = df["source"].str.strip()
df["destination"] = df["destination"].str.strip()
df["cabin_class"] = df["cabin_class"].str.strip().str.title()
df["departure_time"] = df["departure_time"].str.strip().str.title()
df["arrival_time"] = df["arrival_time"].str.strip().str.title()


# Flight code
df["flight_code"] = df["flight"]


# Convert stops to numeric
df["stops"] = df["stops"].map({
    "zero": 0,
    "one": 1,
    "two_or_more": 2
})


# Convert duration from hours to minutes
df["duration_minutes"] = (df["duration"] * 60).round().astype("Int64")


# Convert fare to numeric
df["fare"] = pd.to_numeric(df["price"], errors="coerce")


# Dataset 2 does not provide booking date
df["booking_date"] = pd.NaT

# Dataset 2 does not provide an actual travel date
df["travel_date"] = pd.NaT


# Remove exact duplicates
df = df.drop_duplicates()


# Select common schema
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


# Save cleaned Dataset 2
df.to_csv(
    "C:\\Users\\Kavya\\DeviantX\\SIH-Airfare-Price-Index\\Data\\processed\\airfare_clean_2.csv",
    index=False
)

print("\nDataset 2 cleaning completed.")
print("Final shape:", df.shape)
print("Cleaned file saved successfully.")