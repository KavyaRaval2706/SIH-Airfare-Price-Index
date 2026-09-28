from datetime import date
from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text, select, func
from sqlalchemy.orm import Session

from database import engine, SessionLocal
from models import (
    IndexValue, 
    Route, 
    Airline,
    FareObservation,
    BookingWindow, 
    IndexContribution
)

from schemas import (
    IndexResponse, 
    RouteResponse, 
    AirlineResponse,
    TrendResponse,
    ObservationResponse,
    RouteIndexResponse,
    AirlineIndexResponse,
    BookingWindowResponse,
    ContributionResponse
)


app = FastAPI(
    title="SIH Airfare Price Index API"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return {
        "message": "Airfare Price Index API is running"
    }


@app.get("/api/health")
def health_check():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "database": "connected"
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "connection failed",
            "error": str(e)
        }


@app.get(
    "/api/index",
    response_model=list[IndexResponse]
)
def get_index(
    index_date: date | None = None,
    db: Session = Depends(get_db)
):

    statement = select(IndexValue)

    if index_date is not None:
        statement = statement.where(
            IndexValue.index_date == index_date
        )

    statement = statement.order_by(
        IndexValue.index_date.asc()
    )

    results = db.scalars(statement).all()

    return [
        IndexResponse(
            index_date=row.index_date,
            index_type=row.index_type,
            index_period=row.index_period,
            index_value=float(row.index_value),
            percentage_change=(
                None
                if row.percentage_change is None
                else float(row.percentage_change)
            )
        )
        for row in results
    ]


@app.get(
    "/api/routes",
    response_model=list[RouteResponse]
)
def get_routes(db: Session = Depends(get_db)):

    statement = (
        select(Route)
        .order_by(Route.source_city, Route.destination_city)
    )

    results = db.scalars(statement).all()

    return [
        RouteResponse(
            route_id=row.route_id,
            source_city=row.source_city,
            destination_city=row.destination_city
        )
        for row in results
    ]


@app.get(
    "/api/airlines",
    response_model=list[AirlineResponse]
)
def get_airlines(db: Session = Depends(get_db)):

    statement = (
        select(Airline)
        .order_by(Airline.airline_name)
    )

    results = db.scalars(statement).all()

    return [
        AirlineResponse(
            airline_id=row.airline_id,
            airline_name=row.airline_name,
            airline_code=row.airline_code
        )
        for row in results
    ]


@app.get(
    "/api/trends",
    response_model=list[TrendResponse]
)
def get_trends(db: Session = Depends(get_db)):

    statement = (
        select(IndexValue)
        .where(
            IndexValue.index_type.in_(
                ["daily", "weekly", "monthly"]
            )
        )
        .order_by(IndexValue.index_date.asc())
    )

    results = db.scalars(statement).all()

    return [
        TrendResponse(
            index_date=row.index_date,
            index_type=row.index_type,
            index_value=float(row.index_value),
            percentage_change=(
                None
                if row.percentage_change is None
                else float(row.percentage_change)
            )
        )
        for row in results
    ]


@app.get(
    "/api/observations",
    response_model=list[ObservationResponse]
)
def get_observations(
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db)
):

    statement = (
        select(FareObservation)
        .order_by(FareObservation.observation_id)
        .offset(offset)
        .limit(limit)
    )

    results = db.scalars(statement).all()

    return [
        ObservationResponse(
            observation_id=row.observation_id,
            source_id=row.source_id,
            airline_id=row.airline_id,
            route_id=row.route_id,
            flight_id=row.flight_id,
            cabin_class_id=row.cabin_class_id,
            booking_window_id=row.booking_window_id,
            booking_date=row.booking_date,
            travel_date=row.travel_date,
            departure_time=row.departure_time,
            arrival_time=row.arrival_time,
            duration_minutes=row.duration_minutes,
            stops=row.stops,
            fare=float(row.fare)
        )
        for row in results
    ]


@app.get(
    "/api/routes/{route_id}",
    response_model=list[RouteIndexResponse]
)
def get_route_index(
    route_id: int,
    db: Session = Depends(get_db)
):

    statement = (
        select(IndexValue)
        .where(
            IndexValue.index_type == "route",
            IndexValue.route_id == route_id
        )
        .order_by(IndexValue.index_date.asc())
    )

    results = db.scalars(statement).all()

    return [
        RouteIndexResponse(
            index_date=row.index_date,
            index_value=float(row.index_value),
            percentage_change=(
                None
                if row.percentage_change is None
                else float(row.percentage_change)
            )
        )
        for row in results
    ]


@app.get(
    "/api/airlines/{airline_id}",
    response_model=list[AirlineIndexResponse]
)
def get_airline_index(
    airline_id: int,
    db: Session = Depends(get_db)
):

    statement = (
        select(IndexValue)
        .where(
            IndexValue.index_type == "airline",
            IndexValue.airline_id == airline_id
        )
        .order_by(IndexValue.index_date.asc())
    )

    results = db.scalars(statement).all()

    return [
        AirlineIndexResponse(
            index_date=row.index_date,
            index_value=float(row.index_value),
            percentage_change=(
                None
                if row.percentage_change is None
                else float(row.percentage_change)
            )
        )
        for row in results
    ]


@app.get(
    "/api/booking-windows",
    response_model=list[BookingWindowResponse]
)
def get_booking_windows(
    db: Session = Depends(get_db)
):

    statement = (
        select(
            BookingWindow,
            IndexValue
        )
        .join(
            IndexValue,
            BookingWindow.booking_window_id
            == IndexValue.booking_window_id
        )
        .where(
            IndexValue.index_type == "booking_window"
        )
        .order_by(
            BookingWindow.days_before_departure.asc()
        )
    )

    results = db.execute(statement).all()

    return [
        BookingWindowResponse(
            booking_window_id=window.booking_window_id,
            days_before_departure=window.days_before_departure,
            index_value=float(index.index_value),
            percentage_change=(
                None
                if index.percentage_change is None
                else float(index.percentage_change)
            )
        )
        for window, index in results
    ]


@app.get(
    "/api/contributions",
    response_model=list[ContributionResponse]
)
def get_contributions(
    index_date: date | None = None,
    dimension_type: str | None = None,
    limit: int = Query(default=5, ge=1, le=50),
    db: Session = Depends(get_db)
):
    statement = select(IndexContribution)

    if index_date is not None:
        statement = statement.where(
            IndexContribution.index_date == index_date
        )

    if dimension_type is not None:
        statement = statement.where(
            IndexContribution.dimension_type == dimension_type
        )

    statement = statement.order_by(
        func.abs(IndexContribution.contribution).desc()
    ).limit(limit)

    results = db.scalars(statement).all()

    return [
        ContributionResponse(
            contribution_id=row.contribution_id,
            index_date=row.index_date,
            dimension_type=row.dimension_type,
            dimension_value=row.dimension_value,
            contribution=float(row.contribution)
        )
        for row in results
    ]