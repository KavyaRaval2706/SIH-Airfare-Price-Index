import pandas as pd

df = pd.read_csv("airfare_dataset_100.csv")

# 1. Missing base fare
df.loc[10, "base_fare"] = None

# 2. Missing airline
df.loc[20, "airline"] = None

# 3. Wrong total fare
df.loc[30, "total_fare"] = 99999

# 4. Negative base fare
df.loc[40, "base_fare"] = -500

# 5. Wrong booking window
df.loc[50, "booking_window"] = 100

# 6. Duplicate observation
duplicate_row = df.iloc[[5]]
df = pd.concat([df, duplicate_row], ignore_index=True)

# 7. Invalid route
df.loc[60, "origin"] = df.loc[60, "destination"]

df.to_csv("airfare_raw.csv", index=False)

print("Raw dataset created successfully!")
print("Rows:", len(df))
print("Columns:", len(df.columns))
print("File saved as: airfare_raw.csv")