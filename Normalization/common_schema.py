# Normalization/common_schema.py

NORMALIZED_COLUMNS = [
    "observation_id",
    "source_dataset",
    "airline",
    "flight_code",
    "source",
    "destination",
    "cabin_class",
    "booking_window",
    "booking_date",
    "travel_date",
    "departure_time",
    "arrival_time",
    "duration_minutes",
    "stops",
    "fare",
]


def validate_normalized_columns(df):
    actual_columns = list(df.columns)

    missing_columns = [
        column
        for column in NORMALIZED_COLUMNS
        if column not in actual_columns
    ]

    extra_columns = [
        column
        for column in actual_columns
        if column not in NORMALIZED_COLUMNS
    ]

    if missing_columns or extra_columns:
        raise ValueError(
            "Normalized schema mismatch.\n"
            f"Missing columns: {missing_columns}\n"
            f"Unexpected columns: {extra_columns}\n"
            f"Expected columns: {NORMALIZED_COLUMNS}\n"
            f"Actual columns: {actual_columns}"
        )

    # Force the final column order
    df = df[NORMALIZED_COLUMNS]

    return df