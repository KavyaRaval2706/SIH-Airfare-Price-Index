from datetime import date
from pydantic import BaseModel


class IndexResponse(BaseModel):
    index_date: date | None
    index_type: str
    index_period: str | None
    index_value: float
    percentage_change: float | None


class RouteResponse(BaseModel):
    route_id: int
    source_city: str
    destination_city: str


class AirlineResponse(BaseModel):
    airline_id: int
    airline_name: str
    airline_code: str | None = None


class TrendResponse(BaseModel):
    index_date: date
    index_type: str
    index_value: float
    percentage_change: float | None = None


class ObservationResponse(BaseModel):
    observation_id: int
    source_id: int
    airline_id: int
    route_id: int
    flight_id: int
    cabin_class_id: int
    booking_window_id: int

    booking_date: date
    travel_date: date

    departure_time: str
    arrival_time: str

    duration_minutes: int
    stops: int
    fare: float


class RouteIndexResponse(BaseModel):
    index_date: date
    index_value: float
    percentage_change: float | None = None


class AirlineIndexResponse(BaseModel):
    index_date: date
    index_value: float
    percentage_change: float | None = None


class BookingWindowResponse(BaseModel):
    booking_window_id: int
    days_before_departure: int
    index_value: float
    percentage_change: float | None = None


class ContributionResponse(BaseModel):
    contribution_id: int
    index_date: date
    dimension_type: str
    dimension_value: str
    contribution: float