import pandas as pd
import mysql.connector
import getpass

df = pd.read_csv("airfare_clean.csv")

password = getpass.getpass("Enter your MySQL password: ")

connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password=password,
    database="airfare_project"
)

cursor = connection.cursor()

print("Connected to MySQL successfully!")


airline_ids = {}

for airline in df["airline"].unique():

    cursor.execute(
        "SELECT airline_id FROM airlines WHERE airline_name = %s",
        (airline,)
    )

    result = cursor.fetchone()

    if result:
        airline_id = result[0]

    else:
        cursor.execute(
            "INSERT INTO airlines (airline_name) VALUES (%s)",
            (airline,)
        )

        airline_id = cursor.lastrowid

    airline_ids[airline] = airline_id



route_ids = {}

for _, row in df.iterrows():

    origin = row["origin"]
    destination = row["destination"]

    cursor.execute(
        """
        SELECT route_id
        FROM routes
        WHERE origin = %s AND destination = %s
        """,
        (origin, destination)
    )

    result = cursor.fetchone()

    if result:
        route_id = result[0]

    else:
        cursor.execute(
            """
            INSERT INTO routes (origin, destination)
            VALUES (%s, %s)
            """,
            (origin, destination)
        )

        route_id = cursor.lastrowid

    route_ids[(origin, destination)] = route_id



source_ids = {}

for source in df["source"].unique():

    cursor.execute(
        "SELECT source_id FROM sources WHERE source_name = %s",
        (source,)
    )

    result = cursor.fetchone()

    if result:
        source_id = result[0]

    else:
        cursor.execute(
            "INSERT INTO sources (source_name) VALUES (%s)",
            (source,)
        )

        source_id = cursor.lastrowid

    source_ids[source] = source_id



flight_ids = {}

for _, row in df.iterrows():

    airline = row["airline"]
    origin = row["origin"]
    destination = row["destination"]
    flight_number = row["flight_number"]

    airline_id = airline_ids[airline]
    route_id = route_ids[(origin, destination)]

    cursor.execute(
        """
        SELECT flight_id
        FROM flights
        WHERE airline_id = %s
        AND route_id = %s
        AND flight_number = %s
        """,
        (airline_id, route_id, flight_number)
    )

    result = cursor.fetchone()

    if result:
        flight_id = result[0]

    else:
        cursor.execute(
            """
            INSERT INTO flights
            (airline_id, route_id, flight_number)
            VALUES (%s, %s, %s)
            """,
            (airline_id, route_id, flight_number)
        )

        flight_id = cursor.lastrowid

    flight_ids[
        (airline, origin, destination, flight_number)
    ] = flight_id



for _, row in df.iterrows():

    airline = row["airline"]
    origin = row["origin"]
    destination = row["destination"]
    flight_number = row["flight_number"]

    flight_id = flight_ids[
        (airline, origin, destination, flight_number)
    ]

    source_id = source_ids[row["source"]]

    cursor.execute(
        """
        INSERT INTO fare_observations
        (
            observation_id,
            observation_date,
            source_id,
            flight_id,
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
        )
        VALUES
        (
            %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s
        )
        ON DUPLICATE KEY UPDATE
            observation_id=observation_id
        """,
        (
            row["observation_id"],
            row["observation_date"],
            source_id,
            flight_id,
            row["travel_date"],
            row["departure_time"],
            row["stops"],
            row["booking_window"],
            row["fare_type"],
            row["base_fare"],
            row["taxes"],
            row["mandatory_charges"],
            row["total_fare"],
            row["data_status"]
        )
    )


connection.commit()

print("CSV data imported successfully!")

cursor.close()
connection.close()

print("MySQL connection closed.")