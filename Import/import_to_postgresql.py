import os
import pandas as pd
import psycopg
from dotenv import load_dotenv


# ------------------------------------------------------------
# LOAD ENVIRONMENT VARIABLES
# ------------------------------------------------------------

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


# ------------------------------------------------------------
# FILE PATH
# ------------------------------------------------------------

CSV_PATH = (
    r"C:\Users\Kavya\DeviantX\SIH-Airfare-Price-Index"
    r"\Data\processed\fare_observations.csv"
)


# ------------------------------------------------------------
# LOAD CSV
# ------------------------------------------------------------

print("Loading normalized dataset...")

df = pd.read_csv(
    CSV_PATH,
    low_memory=False
)

print("Rows loaded:", len(df))


# ------------------------------------------------------------
# DATABASE CONNECTION
# ------------------------------------------------------------

print("Connecting to PostgreSQL...")

conn = psycopg.connect(
    host=DB_HOST,
    port=DB_PORT,
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)

print("PostgreSQL connection successful.")


try:

    with conn.cursor() as cur:

        # ----------------------------------------------------
        # 1. DATA SOURCES
        # ----------------------------------------------------

        sources = df["source_dataset"].dropna().unique()

        for source in sources:

            cur.execute(
                """
                INSERT INTO data_sources
                    (source_name, source_type)
                VALUES
                    (%s, %s)
                ON CONFLICT (source_name)
                DO NOTHING;
                """,
                (source, "Dataset")
            )


        # ----------------------------------------------------
        # 2. AIRLINES
        # ----------------------------------------------------

        airlines = df["airline"].dropna().unique()

        for airline in airlines:

            cur.execute(
                """
                INSERT INTO airlines
                    (airline_name)
                VALUES
                    (%s)
                ON CONFLICT (airline_name)
                DO NOTHING;
                """,
                (airline,)
            )


        # ----------------------------------------------------
        # 3. CABIN CLASSES
        # ----------------------------------------------------

        cabin_classes = df["cabin_class"].dropna().unique()

        for cabin_class in cabin_classes:

            cur.execute(
                """
                INSERT INTO cabin_classes
                    (class_name)
                VALUES
                    (%s)
                ON CONFLICT (class_name)
                DO NOTHING;
                """,
                (cabin_class,)
            )


        # ----------------------------------------------------
        # 4. ROUTES
        # ----------------------------------------------------

        routes = (
            df[["source", "destination"]]
            .dropna()
            .drop_duplicates()
        )

        for _, row in routes.iterrows():

            cur.execute(
                """
                INSERT INTO routes
                    (source_city, destination_city)
                VALUES
                    (%s, %s)
                ON CONFLICT (source_city, destination_city)
                DO NOTHING;
                """,
                (
                    row["source"],
                    row["destination"]
                )
            )


        # ----------------------------------------------------
        # 5. FLIGHTS
        # ----------------------------------------------------

        flights = (
            df[["airline", "flight_code"]]
            .dropna()
            .drop_duplicates()
        )

        for _, row in flights.iterrows():

            cur.execute(
                """
                INSERT INTO flights
                    (airline_id, flight_code)
                SELECT
                    airline_id,
                    %s
                FROM airlines
                WHERE airline_name = %s
                ON CONFLICT (airline_id, flight_code)
                DO NOTHING;
                """,
                (
                    row["flight_code"],
                    row["airline"]
                )
            )


        # ----------------------------------------------------
        # 6. BOOKING WINDOWS
        # ----------------------------------------------------

        booking_windows = (
            pd.to_numeric(
                df["booking_window"],
                errors="coerce"
            )
            .dropna()
            .astype(int)
            .unique()
        )

        for window in booking_windows:

            cur.execute(
                """
                INSERT INTO booking_windows
                    (days_before_departure)
                VALUES
                    (%s)
                ON CONFLICT (days_before_departure)
                DO NOTHING;
                """,
                (int(window),)
            )


        # ----------------------------------------------------
        # 7. BUILD LOOKUP DICTIONARIES
        # ----------------------------------------------------

        cur.execute(
            """
            SELECT source_id, source_name
            FROM data_sources;
            """
        )

        source_lookup = {
            name: source_id
            for source_id, name in cur.fetchall()
        }


        cur.execute(
            """
            SELECT airline_id, airline_name
            FROM airlines;
            """
        )

        airline_lookup = {
            name: airline_id
            for airline_id, name in cur.fetchall()
        }


        cur.execute(
            """
            SELECT cabin_class_id, class_name
            FROM cabin_classes;
            """
        )

        cabin_lookup = {
            name: cabin_id
            for cabin_id, name in cur.fetchall()
        }


        cur.execute(
            """
            SELECT route_id, source_city, destination_city
            FROM routes;
            """
        )

        route_lookup = {
            (source, destination): route_id
            for route_id, source, destination in cur.fetchall()
        }


        cur.execute(
            """
            SELECT flight_id, airline_id, flight_code
            FROM flights;
            """
        )

        flight_lookup = {
            (airline_id, flight_code): flight_id
            for flight_id, airline_id, flight_code in cur.fetchall()
        }


        cur.execute(
            """
            SELECT booking_window_id, days_before_departure
            FROM booking_windows;
            """
        )

        booking_window_lookup = {
            days: booking_window_id
            for booking_window_id, days in cur.fetchall()
        }


        # ----------------------------------------------------
        # 8. PREPARE OBSERVATIONS
        # ----------------------------------------------------

        observations = []

        for _, row in df.iterrows():

            source_id = source_lookup[
                row["source_dataset"]
            ]

            airline_id = airline_lookup[
                row["airline"]
            ]

            route_id = route_lookup[
                (
                    row["source"],
                    row["destination"]
                )
            ]


            # Flight is optional
            flight_id = None

            if pd.notna(row["flight_code"]):

                flight_id = flight_lookup.get(
                    (
                        airline_id,
                        row["flight_code"]
                    )
                )


            cabin_class_id = cabin_lookup[
                row["cabin_class"]
            ]


            booking_window_id = booking_window_lookup[
                int(row["booking_window"])
            ]


            # ------------------------------------------------
            # BOOKING DATE
            # ------------------------------------------------

            booking_date = None

            if pd.notna(row["booking_date"]):

                booking_date = pd.to_datetime(
                    row["booking_date"]
                ).date()


            # ------------------------------------------------
            # TRAVEL DATE
            # ------------------------------------------------

            travel_date = None

            if pd.notna(row["travel_date"]):

                travel_date = pd.to_datetime(
                    row["travel_date"]
                ).date()


            # ------------------------------------------------
            # PREPARE OBSERVATION
            #
            # observation_id    -> PostgreSQL identity
            # observation_hash  -> PostgreSQL trigger
            # ------------------------------------------------

            observations.append(
                (
                    source_id,
                    airline_id,
                    route_id,
                    flight_id,
                    cabin_class_id,
                    booking_window_id,
                    booking_date,
                    travel_date,
                    (
                        None
                        if pd.isna(row["departure_time"])
                        else str(row["departure_time"])
                    ),
                    (
                        None
                        if pd.isna(row["arrival_time"])
                        else str(row["arrival_time"])
                    ),
                    int(row["duration_minutes"]),
                    int(row["stops"]),
                    float(row["fare"])
                )
            )


        # ----------------------------------------------------
        # 9. INSERT OBSERVATIONS
        # ----------------------------------------------------

        print("Inserting fare observations...")
        print("Observations prepared:", len(observations))

        cur.executemany(
            """
            INSERT INTO fare_observations (
                source_id,
                airline_id,
                route_id,
                flight_id,
                cabin_class_id,
                booking_window_id,
                booking_date,
                travel_date,
                departure_time,
                arrival_time,
                duration_minutes,
                stops,
                fare
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (observation_hash)
            DO NOTHING;
            """,
            observations
        )


        # ----------------------------------------------------
        # 10. VERIFY HASHES
        # ----------------------------------------------------

        cur.execute(
            """
            SELECT COUNT(*)
            FROM fare_observations
            WHERE observation_hash IS NULL;
            """
        )

        missing_hashes = cur.fetchone()[0]

        if missing_hashes > 0:

            print(
                "\nWARNING:",
                missing_hashes,
                "rows have NULL observation hashes."
            )

            conn.rollback()

            print("Import rolled back.")

            raise RuntimeError(
                    f"{missing_hashes} rows have NULL observation hashes."
            )


        # ----------------------------------------------------
        # COMMIT
        # ----------------------------------------------------

        conn.commit()

        print("\n============================================================")
        print("IMPORT COMPLETED SUCCESSFULLY")
        print("============================================================")
        print("CSV rows processed :", len(observations))
        print("============================================================")


except Exception as e:

    conn.rollback()

    print("\n============================================================")
    print("IMPORT FAILED")
    print("============================================================")
    print("Error:", e)
    print("All database changes have been rolled back.")
    print("============================================================")


finally:

    conn.close()

    print("PostgreSQL connection closed.")