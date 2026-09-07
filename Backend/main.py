from datetime import date

from fastapi import FastAPI, HTTPException
from sqlalchemy import text

from database import engine

app = FastAPI(title="Airfare Price Index API")


@app.get("/")
def root():
    return {"message": "Airfare Price Index API is running"}


@app.get("/api/current")
def get_current_index():
    with engine.connect() as connection:
        query = text("""
            SELECT
                observation_date,
                airfare_index,
                coverage_percent,
                quality_status
            FROM daily_airfare_index
            ORDER BY observation_date DESC
            LIMIT 1
        """)

        result = connection.execute(query).mappings().first()

        if result is None:
            raise HTTPException(
                status_code=404,
                detail="No index data found"
            )

        return {
            "date": result["observation_date"],
            "airfare_index": float(result["airfare_index"]),
            "coverage_percent": float(result["coverage_percent"]),
            "quality_status": result["quality_status"]
        }


@app.get("/api/history")
def get_history(start_date: date, end_date: date):
    if start_date > end_date:
        raise HTTPException(
            status_code=400,
            detail="start_date cannot be after end_date"
        )

    with engine.connect() as connection:
        query = text("""
            SELECT
                observation_date,
                airfare_index,
                coverage_percent,
                quality_status
            FROM daily_airfare_index
            WHERE observation_date BETWEEN :start_date AND :end_date
            ORDER BY observation_date ASC
        """)

        result = connection.execute(
            query,
            {
                "start_date": start_date,
                "end_date": end_date
            }
        ).mappings().all()

        return {
            "start_date": start_date,
            "end_date": end_date,
            "records": [
                {
                    "date": row["observation_date"],
                    "airfare_index": float(row["airfare_index"]),
                    "coverage_percent": float(row["coverage_percent"]),
                    "quality_status": row["quality_status"]
                }
                for row in result
            ]
        }


@app.get("/api/weekly")
def get_weekly_index():
    with engine.connect() as connection:
        query = text("""
            SELECT
                week,
                airfare_index,
                week_on_week_change_percent
            FROM weekly_airfare_index
            ORDER BY week ASC
        """)

        result = connection.execute(query).mappings().all()

        return {
            "records": [
                {
                    "week": row["week"],
                    "airfare_index": float(row["airfare_index"]),
                    "week_on_week_change_percent": (
                        float(row["week_on_week_change_percent"])
                        if row["week_on_week_change_percent"] is not None
                        else None
                    )
                }
                for row in result
            ]
        }


@app.get("/api/monthly")
def get_monthly_index():
    with engine.connect() as connection:
        query = text("""
            SELECT
                month,
                airfare_index,
                month_on_month_change_percent
            FROM monthly_airfare_index
            ORDER BY month ASC
        """)

        result = connection.execute(query).mappings().all()

        return {
            "records": [
                {
                    "month": row["month"],
                    "airfare_index": float(row["airfare_index"]),
                    "month_on_month_change_percent": (
                        float(row["month_on_month_change_percent"])
                        if row["month_on_month_change_percent"] is not None
                        else None
                    )
                }
                for row in result
            ]
        }


@app.get("/api/routes")
def get_routes(route: str | None = None):
    with engine.connect() as connection:

        if route:
            query = text("""
                SELECT
                    observation_date,
                    route,
                    route_airfare_index
                FROM route_wise_airfare_index
                WHERE route = :route
                ORDER BY observation_date ASC
            """)

            result = connection.execute(
                query,
                {"route": route}
            ).mappings().all()

        else:
            query = text("""
                SELECT
                    observation_date,
                    route,
                    route_airfare_index
                FROM route_wise_airfare_index
                ORDER BY observation_date ASC
            """)

            result = connection.execute(query).mappings().all()

        return {
            "records": [
                {
                    "date": row["observation_date"],
                    "route": row["route"],
                    "route_wise_airfare_index": float(row["route_airfare_index"])
                }
                for row in result
            ]
        }
