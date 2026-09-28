from pathlib import Path

import pandas as pd
import numpy as np


# ============================================================
# 1. PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

CALCULATION_FOLDER = PROJECT_ROOT / "calculation"


# ============================================================
# 2. FILE PATHS
# ============================================================

FILES = {
    "daily": PROJECT_ROOT / "Calculation" / "Output" / "daily_airfare_index.csv",
    "weekly": PROJECT_ROOT / "Calculation" / "Output" / "weekly_airfare_index.csv",
    "monthly": PROJECT_ROOT / "Calculation" / "Output" / "monthly_airfare_index.csv",
    "route": PROJECT_ROOT / "Calculation" / "Output" / "route_wise_airfare_index.csv",
    "airline": PROJECT_ROOT / "Calculation" / "Output" / "airline_wise_airfare_index.csv",
    "booking_window": PROJECT_ROOT / "Calculation" / "Output" / "booking_window_index.csv",
    "contributions": PROJECT_ROOT / "Calculation" / "Output" / "index_contributions.csv",
}


# ============================================================
# 3. EXPECTED STRUCTURE
# ============================================================

EXPECTED_COLUMNS = {
    "daily": [
        "index_date",
        "index_value",
        "percentage_change",
    ],

    "weekly": [
        "index_week",
        "index_value",
        "percentage_change",
    ],

    "monthly": [
        "index_month",
        "index_value",
        "percentage_change",
    ],

    "route": [
        "index_date",
        "route_id",
        "source_city",
        "destination_city",
        "index_value",
        "percentage_change",
    ],

    "airline": [
        "index_date",
        "airline_id",
        "airline_name",
        "index_value",
        "percentage_change",
    ],

    "booking_window": [
        "booking_window",
        "median_fare",
        "index_value",
        "percentage_change",
    ],

    "contributions": [
        "index_date",
        "dimension_type",
        "dimension_value",
        "contribution",
    ],
}


# ============================================================
# 4. EXPECTED ROW COUNTS
# ============================================================

EXPECTED_ROW_COUNTS = {
    "daily": 50,
    "weekly": 8,
    "monthly": 3,
    "booking_window": 50,
}


# ============================================================
# 5. HELPER FUNCTIONS
# ============================================================

total_checks = 0
passed_checks = 0
failed_checks = 0


def check(condition, message):
    global total_checks
    global passed_checks
    global failed_checks

    total_checks += 1

    if condition:
        print(f"  [PASS] {message}")
        passed_checks += 1
    else:
        print(f"  [FAIL] {message}")
        failed_checks += 1


def load_csv(file_key):
    file_path = FILES[file_key]

    check(
        file_path.exists(),
        f"{file_key}: file exists"
    )

    if not file_path.exists():
        return None

    dataframe = pd.read_csv(file_path)

    print(
        f"  {file_key}: "
        f"{len(dataframe):,} rows × "
        f"{len(dataframe.columns)} columns"
    )

    return dataframe


# ============================================================
# 6. LOAD ALL FILES
# ============================================================

print()
print("=" * 70)
print("AIRFARE CALCULATION OUTPUT VALIDATION")
print("=" * 70)

data = {}

for file_key in FILES:
    print()
    print(f"Loading {file_key}...")
    data[file_key] = load_csv(file_key)


# ============================================================
# 7. COLUMN VALIDATION
# ============================================================

print()
print("=" * 70)
print("COLUMN VALIDATION")
print("=" * 70)

for file_key, expected_columns in EXPECTED_COLUMNS.items():

    dataframe = data[file_key]

    if dataframe is None:
        continue

    actual_columns = dataframe.columns.tolist()

    check(
        actual_columns == expected_columns,
        f"{file_key}: columns are correct"
    )

    if actual_columns != expected_columns:

        print(f"    Expected: {expected_columns}")
        print(f"    Actual:   {actual_columns}")


# ============================================================
# 8. ROW COUNT VALIDATION
# ============================================================

print()
print("=" * 70)
print("ROW COUNT VALIDATION")
print("=" * 70)

for file_key, expected_count in EXPECTED_ROW_COUNTS.items():

    dataframe = data[file_key]

    if dataframe is None:
        continue

    actual_count = len(dataframe)

    check(
        actual_count == expected_count,
        f"{file_key}: expected {expected_count:,} rows, "
        f"found {actual_count:,}"
    )


# ============================================================
# 9. MISSING VALUE VALIDATION
# ============================================================

print()
print("=" * 70)
print("MISSING VALUE VALIDATION")
print("=" * 70)

for file_key, dataframe in data.items():

    if dataframe is None:
        continue

    missing_total = int(
        dataframe.isna().sum().sum()
    )

    # percentage_change is expected to have one NaN
    # for the first observation of each applicable series.
    if file_key in {
        "daily",
        "weekly",
        "monthly",
    }:

        allowed_missing = 1

    elif file_key == "route":

        # One first value per route.
        allowed_missing = (
            dataframe["route_id"].nunique()
        )

    elif file_key == "airline":

        # One first value per airline.
        allowed_missing = (
            dataframe["airline_id"].nunique()
        )

    elif file_key == "booking_window":

        # T+1 has no previous booking window.
        allowed_missing = 1

    else:

        allowed_missing = 0

    check(
        missing_total == allowed_missing,
        f"{file_key}: missing values = "
        f"{missing_total} "
        f"(expected {allowed_missing})"
    )

    if missing_total > 0:

        print("    Missing values by column:")

        missing_by_column = (
            dataframe.isna()
            .sum()
        )

        for column, count in missing_by_column.items():

            if count > 0:
                print(
                    f"      {column}: {count}"
                )


# ============================================================
# 10. DUPLICATE ROW VALIDATION
# ============================================================

print()
print("=" * 70)
print("DUPLICATE VALIDATION")
print("=" * 70)

for file_key, dataframe in data.items():

    if dataframe is None:
        continue

    duplicate_count = int(
        dataframe.duplicated().sum()
    )

    check(
        duplicate_count == 0,
        f"{file_key}: duplicate rows = "
        f"{duplicate_count}"
    )


# ============================================================
# 11. NUMERIC INDEX VALIDATION
# ============================================================

print()
print("=" * 70)
print("INDEX VALUE VALIDATION")
print("=" * 70)

for file_key in [
    "daily",
    "weekly",
    "monthly",
    "route",
    "airline",
    "booking_window",
]:

    dataframe = data[file_key]

    if dataframe is None:
        continue

    invalid_index_count = int(
        (
            ~np.isfinite(
                pd.to_numeric(
                    dataframe["index_value"],
                    errors="coerce"
                )
            )
            |
            (
                pd.to_numeric(
                    dataframe["index_value"],
                    errors="coerce"
                )
                <= 0
            )
        ).sum()
    )

    check(
        invalid_index_count == 0,
        f"{file_key}: invalid index values = "
        f"{invalid_index_count}"
    )


# ============================================================
# 12. PERCENTAGE CHANGE VALIDATION
# ============================================================

print()
print("=" * 70)
print("PERCENTAGE CHANGE VALIDATION")
print("=" * 70)

for file_key in [
    "daily",
    "weekly",
    "monthly",
    "route",
    "airline",
    "booking_window",
]:

    dataframe = data[file_key]

    if dataframe is None:
        continue

    percentage_change = pd.to_numeric(
        dataframe["percentage_change"],
        errors="coerce"
    )

    invalid_percentage_change = (
        percentage_change.notna()
        &
        ~np.isfinite(
            percentage_change
        )
    ).sum()

    check(
        invalid_percentage_change == 0,
        f"{file_key}: invalid percentage changes = "
        f"{invalid_percentage_change}"
    )


# ============================================================
# 13. DAILY DATE VALIDATION
# ============================================================

print()
print("=" * 70)
print("DAILY DATE VALIDATION")
print("=" * 70)

daily_index = data["daily"]

if daily_index is not None:

    daily_index["index_date"] = pd.to_datetime(
        daily_index["index_date"],
        errors="coerce"
    )

    invalid_dates = int(
        daily_index["index_date"].isna().sum()
    )

    check(
        invalid_dates == 0,
        f"daily: invalid dates = {invalid_dates}"
    )

    unique_dates = (
        daily_index["index_date"]
        .nunique()
    )

    check(
        unique_dates == len(daily_index),
        "daily: every row has a unique date"
    )

    date_range_days = (
        daily_index["index_date"].max()
        - daily_index["index_date"].min()
    ).days + 1

    check(
        date_range_days == len(daily_index),
        "daily: dates form a continuous daily range"
    )

    print(
        f"  Daily date range: "
        f"{daily_index['index_date'].min().date()} "
        f"to "
        f"{daily_index['index_date'].max().date()}"
    )


# ============================================================
# 14. BOOKING WINDOW VALIDATION
# ============================================================

print()
print("=" * 70)
print("BOOKING WINDOW VALIDATION")
print("=" * 70)

booking_window_index = data["booking_window"]

if booking_window_index is not None:

    booking_window_values = sorted(
        booking_window_index[
            "booking_window"
        ]
        .dropna()
        .astype(int)
        .unique()
        .tolist()
    )

    expected_booking_windows = list(
        range(1, 51)
    )

    check(
        booking_window_values
        == expected_booking_windows,
        "booking windows are exactly T+1 through T+50"
    )

    check(
        len(booking_window_index) == 50,
        "exactly 50 booking-window index rows exist"
    )

    check(
        booking_window_index[
            "booking_window"
        ].nunique() == 50,
        "each booking window appears exactly once"
    )

    check(
        (
            pd.to_numeric(
                booking_window_index["median_fare"],
                errors="coerce"
            )
            > 0
        ).all(),
        "all booking-window median fares are positive"
    )

    t1_index = booking_window_index.loc[
        booking_window_index["booking_window"] == 1,
        "index_value"
    ]

    if len(t1_index) == 1:

        check(
            np.isclose(
                float(t1_index.iloc[0]),
                100.0
            ),
            "T+1 booking-window index = 100"
        )


# ============================================================
# 15. ROUTE VALIDATION
# ============================================================

print()
print("=" * 70)
print("ROUTE-WISE VALIDATION")
print("=" * 70)

route_index = data["route"]

if route_index is not None:

    check(
        route_index["route_id"].notna().all(),
        "route: no missing route IDs"
    )

    check(
        (
            route_index["source_city"]
            != route_index["destination_city"]
        ).all(),
        "route: source and destination cities differ"
    )

    route_count = (
        route_index["route_id"]
        .nunique()
    )

    print(
        f"  Unique routes represented: "
        f"{route_count}"
    )


# ============================================================
# 16. AIRLINE VALIDATION
# ============================================================

print()
print("=" * 70)
print("AIRLINE-WISE VALIDATION")
print("=" * 70)

airline_index = data["airline"]

if airline_index is not None:

    check(
        airline_index["airline_id"].notna().all(),
        "airline: no missing airline IDs"
    )

    check(
        airline_index["airline_name"].notna().all(),
        "airline: no missing airline names"
    )

    airline_count = (
        airline_index["airline_id"]
        .nunique()
    )

    print(
        f"  Unique airlines represented: "
        f"{airline_count}"
    )


# ============================================================
# 17. CONTRIBUTION VALIDATION
# ============================================================

print()
print("=" * 70)
print("CONTRIBUTION VALIDATION")
print("=" * 70)

contributions = data["contributions"]

if contributions is not None:

    check(
        contributions["dimension_type"]
        .isin(
            [
                "route",
                "airline",
                "booking_window"
            ]
        )
        .all(),
        "contributions: valid dimension types"
    )

    check(
        contributions["dimension_value"]
        .notna()
        .all(),
        "contributions: no missing dimension values"
    )

    check(
        pd.to_numeric(
            contributions["contribution"],
            errors="coerce"
        ).notna().all(),
        "contributions: all contribution values are numeric"
    )

    print(
        "  Contribution types:"
    )

    print(
        contributions[
            "dimension_type"
        ]
        .value_counts()
        .to_string()
    )

    print(
        f"  Total contribution rows: "
        f"{len(contributions):,}"
    )


# ============================================================
# 18. CONTRIBUTION DATE ALIGNMENT
# ============================================================

print()
print("=" * 70)
print("CONTRIBUTION DATE ALIGNMENT")
print("=" * 70)

if (
    contributions is not None
    and daily_index is not None
):

    contributions["index_date"] = pd.to_datetime(
        contributions["index_date"],
        errors="coerce"
    )

    daily_dates = set(
        daily_index["index_date"]
        .dropna()
    )

    contribution_dates = set(
        contributions["index_date"]
        .dropna()
    )

    invalid_contribution_dates = (
        contribution_dates - daily_dates
    )

    check(
        len(invalid_contribution_dates) == 0,
        "all contribution dates exist in daily index"
    )


# ============================================================
# 19. FINAL RESULT
# ============================================================

print()
print("=" * 70)
print("FINAL VALIDATION RESULT")
print("=" * 70)

print(
    f"Total checks : {total_checks}"
)

print(
    f"Passed       : {passed_checks}"
)

print(
    f"Failed       : {failed_checks}"
)

print("=" * 70)

if failed_checks == 0:

    print(
        "VALIDATION PASSED: "
        "All calculation-output checks passed."
    )

else:

    print(
        "VALIDATION FAILED: "
        "Review the [FAIL] checks above."
    )