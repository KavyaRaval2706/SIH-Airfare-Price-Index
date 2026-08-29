import pandas as pd
import random
from datetime import date, timedelta

random.seed(42)

airlines = [
    "IndiGo",
    "Air India",
    "Akasa Air",
    "Air India Express",
    "SpiceJet"
]

routes = [
    ("AMD", "DEL", 5000),
    ("AMD", "BOM", 4200),
    ("AMD", "BLR", 5500),
    ("DEL", "BOM", 4800),
    ("DEL", "BLR", 5600),
    ("DEL", "MAA", 5500),
    ("BOM", "BLR", 4300),
    ("BOM", "DEL", 4800),
    ("BLR", "MAA", 4000),
    ("DEL", "CCU", 5200)
]

departure_times = [
    "06:30",
    "08:00",
    "09:45",
    "11:30",
    "13:15",
    "15:30",
    "18:00",
    "20:30"
]

fare_types = [
    "Economy",
    "Premium Economy"
]

booking_windows = [
    60,
    45,
    30,
    21,
    15,
    7,
    3,
    1
]



data = []

start_observation_date = date(2026, 8, 1)

for i in range(100):

    observation_date = start_observation_date + timedelta(
        days=random.randint(0, 20)
    )

    airline = random.choice(airlines)

    origin, destination, base_route_price = random.choice(routes)

    booking_window = random.choice(booking_windows)

    travel_date = observation_date + timedelta(
        days=booking_window
    )

    flight_number = random.choice([
        "6E101",
        "6E201",
        "AI402",
        "AI512",
        "QP1401",
        "QP1102",
        "IX321",
        "SG501"
    ])

    departure_time = random.choice(departure_times)

    stops = random.choice([0, 0, 0, 1])

    fare_type = random.choice(fare_types)

    if fare_type == "Premium Economy":
        fare_multiplier = 1.25
    else:
        fare_multiplier = 1.0

    if booking_window >= 45:
        booking_multiplier = 0.85
    elif booking_window >= 30:
        booking_multiplier = 0.90
    elif booking_window >= 21:
        booking_multiplier = 0.95
    elif booking_window >= 15:
        booking_multiplier = 1.00
    elif booking_window >= 7:
        booking_multiplier = 1.10
    elif booking_window >= 3:
        booking_multiplier = 1.20
    else:
        booking_multiplier = 1.35

    airline_multiplier = {
        "IndiGo": 1.00,
        "Air India": 1.05,
        "Akasa Air": 0.95,
        "Air India Express": 0.92,
        "SpiceJet": 0.90
    }

    base_fare = (
        base_route_price
        * booking_multiplier
        * fare_multiplier
        * airline_multiplier[airline]
    )

    random_variation = random.uniform(0.90, 1.10)

    base_fare = int(base_fare * random_variation)

    taxes = int(base_fare * random.uniform(0.10, 0.15))

    mandatory_charges = random.choice([
        150,
        180,
        200,
        220,
        250
    ])

    total_fare = base_fare + taxes + mandatory_charges

    observation_id = f"OBS{i + 1:03d}"

    source = "Synthetic Demo"

    data_status = "Observed"

    data.append([
        observation_id,
        observation_date,
        source,
        airline,
        flight_number,
        origin,
        destination,
        travel_date,
        departure_time,
        stops,
        booking_window,
        fare_type,
        base_fare,
        taxes,
        mandatory_charges,
        total_fare,
        data_status
    ])


columns = [
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

df = pd.DataFrame(data, columns=columns)

df["observation_date"] = pd.to_datetime(
    df["observation_date"]
)

df["travel_date"] = pd.to_datetime(
    df["travel_date"]
)

df["booking_window"] = (
    df["travel_date"] - df["observation_date"]
).dt.days

df["total_fare"] = (
    df["base_fare"]
    + df["taxes"]
    + df["mandatory_charges"]
)

df.to_csv(
    "airfare_dataset_100.csv",
    index=False
)

print("Dataset created successfully!")
print()
print("Rows:", len(df))
print("Columns:", len(df.columns))
print()
print(df.head(10))
print()
print("File saved as: airfare_dataset_100.csv")