from pathlib import Path
import os

import pandas as pd
import psycopg
from dotenv import load_dotenv


# ============================================================
# 1. PATHS
# ============================================================

# Project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Calculation output directory
OUTPUT_DIR = PROJECT_ROOT / "Calculation" / "Output"


# ============================================================
# 2. DATABASE CONFIGURATION
# ============================================================

load_dotenv(PROJECT_ROOT / ".env")

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "dbname": os.getenv("DB_NAME", "airfare_project"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD"),
}


# ============================================================
# 3. REQUIRED FILES
# ============================================================

FILES = {
    "daily": OUTPUT_DIR / "daily_airfare_index.csv",
    "weekly": OUTPUT_DIR / "weekly_airfare_index.csv",
    "monthly": OUTPUT_DIR / "monthly_airfare_index.csv",
    "route": OUTPUT_DIR / "route_wise_airfare_index.csv",
    "airline": OUTPUT_DIR / "airline_wise_airfare_index.csv",
    "booking_window": OUTPUT_DIR / "booking_window_index.csv",
    "contributions": OUTPUT_DIR / "index_contributions.csv",
}


# ============================================================
# 4. CHECK FILES
# ============================================================

print("=" * 70)
print("CALCULATION OUTPUT IMPORT")
print("=" * 70)

print(f"\nProject root : {PROJECT_ROOT}")
print(f"Output dir  : {OUTPUT_DIR}")

for name, path in FILES.items():
    if not path.exists():
        raise FileNotFoundError(
            f"\nMissing {name} output file:\n{path}"
        )

    print(f"[FOUND] {path.name}")


# ============================================================
# 5. LOAD CSV FILES
# ============================================================

print("\nLoading calculation outputs...")

daily = pd.read_csv(FILES["daily"])
weekly = pd.read_csv(FILES["weekly"])
monthly = pd.read_csv(FILES["monthly"])
route = pd.read_csv(FILES["route"])
airline = pd.read_csv(FILES["airline"])
booking_window = pd.read_csv(FILES["booking_window"])
contributions = pd.read_csv(FILES["contributions"])


print("\nRows loaded:")
print(f"  Daily          : {len(daily):,}")
print(f"  Weekly         : {len(weekly):,}")
print(f"  Monthly        : {len(monthly):,}")
print(f"  Route-wise     : {len(route):,}")
print(f"  Airline-wise   : {len(airline):,}")
print(f"  Booking-window : {len(booking_window):,}")
print(f"  Contributions   : {len(contributions):,}")


# ============================================================
# 6. VALIDATE EXPECTED COLUMNS
# ============================================================

EXPECTED_COLUMNS = {
    "daily": {
        "index_date",
        "index_value",
        "percentage_change",
    },

    "weekly": {
        "index_week",
        "index_value",
        "percentage_change",
    },

    "monthly": {
        "index_month",
        "index_value",
        "percentage_change",
    },

    "route": {
        "index_date",
        "route_id",
        "source_city",
        "destination_city",
        "index_value",
        "percentage_change",
    },

    "airline": {
        "index_date",
        "airline_id",
        "airline_name",
        "index_value",
        "percentage_change",
    },

    "booking_window": {
        "median_fare",
        "booking_window",
        "index_value",
        "percentage_change",
    },

    "contributions": {
        "index_date",
        "dimension_type",
        "dimension_value",
        "contribution",
    },
}


DATAFRAMES = {
    "daily": daily,
    "weekly": weekly,
    "monthly": monthly,
    "route": route,
    "airline": airline,
    "booking_window": booking_window,
    "contributions": contributions,
}


print("\nChecking columns...")

for name, df in DATAFRAMES.items():

    actual = set(df.columns)
    expected = EXPECTED_COLUMNS[name]

    missing = expected - actual

    if missing:
        raise ValueError(
            f"{name} CSV is missing columns: {sorted(missing)}"
        )

    print(f"[PASS] {name}")


# ============================================================
# 7. CONNECT TO POSTGRESQL
# ============================================================

print("\nConnecting to PostgreSQL...")

conn = psycopg.connect(**DB_CONFIG)

print("[PASS] PostgreSQL connection established")


# ============================================================
# 8. HELPER: BOOKING WINDOW LOOKUP
# ============================================================

def get_booking_window_id(cur, days_before_departure):
    """
    Convert days_before_departure into the actual
    booking_window_id from the booking_windows table.

    IMPORTANT:
    booking_window_id is NOT assumed to equal
    days_before_departure.
    """

    cur.execute(
        """
        SELECT booking_window_id
        FROM booking_windows
        WHERE days_before_departure = %s
        """,
        (int(days_before_departure),)
    )

    row = cur.fetchone()

    if row is None:
        raise ValueError(
            f"No booking window found for T+{days_before_departure}"
        )

    return row[0]


# ============================================================
# 9. INSERT INDEX VALUES
# ============================================================

def insert_index_value(
    cur,
    index_date,
    index_type,
    index_period,
    route_id,
    airline_id,
    booking_window_id,
    index_value,
    percentage_change,
):
    """
    Insert or update an index value.

    The conflict rule depends on the type of index:
      daily/weekly/monthly -> index_type + index_date
      route                -> index_type + index_date + route_id
      airline              -> index_type + index_date + airline_id
      booking_window       -> index_type + booking_window_id
    """

    if index_type in ("daily", "weekly", "monthly"):

        conflict_clause = """
            ON CONFLICT (index_type, index_date)
            WHERE index_type IN ('daily', 'weekly', 'monthly')
        """

    elif index_type == "route":

        conflict_clause = """
            ON CONFLICT (index_type, index_date, route_id)
            WHERE index_type = 'route'
        """

    elif index_type == "airline":

        conflict_clause = """
            ON CONFLICT (index_type, index_date, airline_id)
            WHERE index_type = 'airline'
        """

    elif index_type == "booking_window":

        conflict_clause = """
            ON CONFLICT (index_type, booking_window_id)
            WHERE index_type = 'booking_window'
        """

    else:
        raise ValueError(
            f"Unsupported index type: {index_type}"
        )

    query = f"""
        INSERT INTO index_values (
            index_date,
            index_type,
            index_period,
            route_id,
            airline_id,
            booking_window_id,
            index_value,
            percentage_change
        )
        VALUES (
            %s, %s, %s, %s,
            %s, %s, %s, %s
        )

        {conflict_clause}

        DO UPDATE SET
            index_period = EXCLUDED.index_period,
            index_value = EXCLUDED.index_value,
            percentage_change = EXCLUDED.percentage_change
    """

    cur.execute(
        query,
        (
            index_date,
            index_type,
            index_period,
            route_id,
            airline_id,
            booking_window_id,
            index_value,
            percentage_change,
        ),
    )


# ============================================================
# 10. IMPORT DAILY INDEX
# ============================================================

print("\nImporting daily index...")

with conn.cursor() as cur:

    for _, row in daily.iterrows():

        insert_index_value(
            cur=cur,
            index_date=pd.to_datetime(
                row["index_date"]
            ).date(),

            index_type="daily",

            index_period=None,

            route_id=None,

            airline_id=None,

            booking_window_id=None,

            index_value=float(row["index_value"]),

            percentage_change=(
                None
                if pd.isna(row["percentage_change"])
                else float(row["percentage_change"])
            ),
        )

print(f"[PASS] Daily index: {len(daily):,} rows")


# ============================================================
# 11. IMPORT WEEKLY INDEX
# ============================================================

print("\nImporting weekly index...")

with conn.cursor() as cur:

    for _, row in weekly.iterrows():

        # Example:
        # 2025-01-06/2025-01-12
        #
        # Store the period text in index_period.
        # Use the first date as index_date.

        period = str(row["index_week"])

        start_date = pd.to_datetime(
            period.split("/")[0]
        ).date()

        insert_index_value(
            cur=cur,

            index_date=start_date,

            index_type="weekly",

            index_period=period,

            route_id=None,

            airline_id=None,

            booking_window_id=None,

            index_value=float(row["index_value"]),

            percentage_change=(
                None
                if pd.isna(row["percentage_change"])
                else float(row["percentage_change"])
            ),
        )

print(f"[PASS] Weekly index: {len(weekly):,} rows")


# ============================================================
# 12. IMPORT MONTHLY INDEX
# ============================================================

print("\nImporting monthly index...")

with conn.cursor() as cur:

    for _, row in monthly.iterrows():

        # Example:
        # 2025-01
        #
        # Store "2025-01" in index_period
        # and 2025-01-01 in index_date.

        period = str(row["index_month"])

        start_date = pd.to_datetime(
            period + "-01"
        ).date()

        insert_index_value(
            cur=cur,

            index_date=start_date,

            index_type="monthly",

            index_period=period,

            route_id=None,

            airline_id=None,

            booking_window_id=None,

            index_value=float(row["index_value"]),

            percentage_change=(
                None
                if pd.isna(row["percentage_change"])
                else float(row["percentage_change"])
            ),
        )

print(f"[PASS] Monthly index: {len(monthly):,} rows")


# ============================================================
# 13. IMPORT ROUTE-WISE INDEX
# ============================================================

print("\nImporting route-wise index...")

with conn.cursor() as cur:

    for _, row in route.iterrows():

        insert_index_value(
            cur=cur,

            index_date=pd.to_datetime(
                row["index_date"]
            ).date(),

            index_type="route",

            index_period=None,

            route_id=int(row["route_id"]),

            airline_id=None,

            booking_window_id=None,

            index_value=float(row["index_value"]),

            percentage_change=(
                None
                if pd.isna(row["percentage_change"])
                else float(row["percentage_change"])
            ),
        )

print(f"[PASS] Route-wise index: {len(route):,} rows")


# ============================================================
# 14. IMPORT AIRLINE-WISE INDEX
# ============================================================

print("\nImporting airline-wise index...")

with conn.cursor() as cur:

    for _, row in airline.iterrows():

        insert_index_value(
            cur=cur,

            index_date=pd.to_datetime(
                row["index_date"]
            ).date(),

            index_type="airline",

            index_period=None,

            route_id=None,

            airline_id=int(row["airline_id"]),

            booking_window_id=None,

            index_value=float(row["index_value"]),

            percentage_change=(
                None
                if pd.isna(row["percentage_change"])
                else float(row["percentage_change"])
            ),
        )

print(f"[PASS] Airline-wise index: {len(airline):,} rows")


# ============================================================
# 15. IMPORT BOOKING-WINDOW INDEX
# ============================================================

print("\nImporting booking-window index...")

with conn.cursor() as cur:

    for _, row in booking_window.iterrows():

        days = int(row["booking_window"])

        booking_window_id = get_booking_window_id(
            cur,
            days
        )

        insert_index_value(
            cur=cur,

            # Booking-window index is NOT date-based
            index_date=None,

            index_type="booking_window",

            index_period=f"T+{days}",

            route_id=None,

            airline_id=None,

            booking_window_id=booking_window_id,

            index_value=float(row["index_value"]),

            percentage_change=(
                None
                if pd.isna(row["percentage_change"])
                else float(row["percentage_change"])
            ),
        )

print(
    f"[PASS] Booking-window index: "
    f"{len(booking_window):,} rows"
)


# ============================================================
# 16. IMPORT CONTRIBUTIONS
# ============================================================

print("\nImporting index contributions...")

with conn.cursor() as cur:

    for _, row in contributions.iterrows():

        cur.execute(
            """
            INSERT INTO index_contributions (
                index_date,
                dimension_type,
                dimension_value,
                contribution
            )
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (
                index_date,
                dimension_type,
                dimension_value
            )
            DO UPDATE SET
                contribution = EXCLUDED.contribution
            """,
            (
                pd.to_datetime(
                    row["index_date"]
                ).date(),

                str(row["dimension_type"]),

                str(row["dimension_value"]),

                float(row["contribution"]),
            ),
        )

print(
    f"[PASS] Contributions: "
    f"{len(contributions):,} rows"
)


# ============================================================
# 17. COMMIT
# ============================================================

conn.commit()

print("\nTransaction committed successfully.")


# ============================================================
# 18. FINAL DATABASE COUNTS
# ============================================================

print("\nChecking database counts...")

with conn.cursor() as cur:

    cur.execute(
        """
        SELECT index_type, COUNT(*)
        FROM index_values
        GROUP BY index_type
        ORDER BY index_type
        """
    )

    index_counts = cur.fetchall()

    print("\nindex_values:")

    for index_type, count in index_counts:
        print(
            f"  {index_type:<16} : {count:,}"
        )

    cur.execute(
        """
        SELECT COUNT(*)
        FROM index_contributions
        """
    )

    contribution_count = cur.fetchone()[0]

    print(
        f"\nindex_contributions : "
        f"{contribution_count:,}"
    )


# ============================================================
# 19. CLOSE CONNECTION
# ============================================================

conn.close()

print("\n" + "=" * 70)
print("CALCULATION OUTPUT IMPORT COMPLETED SUCCESSFULLY")
print("=" * 70)