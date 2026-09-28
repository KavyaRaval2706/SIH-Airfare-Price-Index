from sqlalchemy import BigInteger, Date, Integer, Numeric, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class IndexValue(Base):
    __tablename__ = "index_values"

    index_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True
    )

    index_date: Mapped[Date | None] = mapped_column(
        Date,
        nullable=True
    )

    index_type: Mapped[str] = mapped_column(
        String(30)
    )

    index_period: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )

    route_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    airline_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    booking_window_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    index_value: Mapped[float] = mapped_column(
        Numeric(12, 4)
    )

    percentage_change: Mapped[float | None] = mapped_column(
        Numeric(10, 4),
        nullable=True
    )

class Route(Base):
    __tablename__ = "routes"

    route_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    source_city: Mapped[str] = mapped_column(
        String
    )

    destination_city: Mapped[str] = mapped_column(
        String
    )


class Airline(Base):
    __tablename__ = "airlines"

    airline_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    airline_name: Mapped[str] = mapped_column(
        String
    )

    airline_code: Mapped[str] = mapped_column(
        String
    )


class FareObservation(Base):
    __tablename__ = "fare_observations"

    observation_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True
    )

    source_id: Mapped[int] = mapped_column(Integer)
    airline_id: Mapped[int] = mapped_column(Integer)
    route_id: Mapped[int] = mapped_column(Integer)
    flight_id: Mapped[int] = mapped_column(Integer)
    cabin_class_id: Mapped[int] = mapped_column(Integer)
    booking_window_id: Mapped[int] = mapped_column(Integer)

    booking_date: Mapped[Date] = mapped_column(Date)
    travel_date: Mapped[Date] = mapped_column(Date)

    departure_time: Mapped[str] = mapped_column(String)
    arrival_time: Mapped[str] = mapped_column(String)

    duration_minutes: Mapped[int] = mapped_column(Integer)
    stops: Mapped[int] = mapped_column(Integer)

    fare: Mapped[float] = mapped_column(Numeric)


class BookingWindow(Base):
    __tablename__ = "booking_windows"

    booking_window_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    days_before_departure: Mapped[int] = mapped_column(
        Integer
    )


class IndexContribution(Base):
    __tablename__ = "index_contributions"

    contribution_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    index_date: Mapped[Date] = mapped_column(Date)
    dimension_type: Mapped[str] = mapped_column(String(30))
    dimension_value: Mapped[str] = mapped_column(String(100))
    contribution: Mapped[float] = mapped_column(Numeric(12, 4))