-- ============================================================
-- SIH Airfare Price Index
-- PostgreSQL Database Schema
-- ============================================================

-- ------------------------------------------------------------
-- 1. DATA SOURCES
-- ------------------------------------------------------------

CREATE TABLE data_sources (
    source_id SERIAL PRIMARY KEY,
    source_name VARCHAR(100) NOT NULL UNIQUE,
    source_type VARCHAR(50),
    description TEXT
);


-- ------------------------------------------------------------
-- 2. AIRLINES
-- ------------------------------------------------------------

CREATE TABLE airlines (
    airline_id SERIAL PRIMARY KEY,
    airline_name VARCHAR(100) NOT NULL UNIQUE,
    airline_code VARCHAR(20)
);


-- ------------------------------------------------------------
-- 3. ROUTES
-- ------------------------------------------------------------

CREATE TABLE routes (
    route_id SERIAL PRIMARY KEY,
    source_city VARCHAR(100) NOT NULL,
    destination_city VARCHAR(100) NOT NULL,

    CONSTRAINT unique_route
        UNIQUE (source_city, destination_city),

    CONSTRAINT different_cities
        CHECK (source_city <> destination_city)
);


-- ------------------------------------------------------------
-- 4. FLIGHTS
-- ------------------------------------------------------------

CREATE TABLE flights (
    flight_id SERIAL PRIMARY KEY,

    airline_id INTEGER NOT NULL,
    flight_code VARCHAR(30) NOT NULL,

    CONSTRAINT fk_flight_airline
        FOREIGN KEY (airline_id)
        REFERENCES airlines(airline_id),

    CONSTRAINT unique_airline_flight
        UNIQUE (airline_id, flight_code)
);


-- ------------------------------------------------------------
-- 5. CABIN CLASSES
-- ------------------------------------------------------------

CREATE TABLE cabin_classes (
    cabin_class_id SERIAL PRIMARY KEY,
    class_name VARCHAR(50) NOT NULL UNIQUE
);


-- ------------------------------------------------------------
-- 6. BOOKING WINDOWS
-- ------------------------------------------------------------

CREATE TABLE booking_windows (
    booking_window_id SERIAL PRIMARY KEY,

    days_before_departure INTEGER NOT NULL UNIQUE,

    CONSTRAINT positive_booking_window
        CHECK (days_before_departure >= 1)
);


-- ------------------------------------------------------------
-- 7. FARE OBSERVATIONS
-- ------------------------------------------------------------

CREATE TABLE fare_observations (
    observation_id BIGINT PRIMARY KEY,

    source_id INTEGER NOT NULL,
    airline_id INTEGER NOT NULL,
    route_id INTEGER NOT NULL,
    flight_id INTEGER,
    cabin_class_id INTEGER NOT NULL,
    booking_window_id INTEGER NOT NULL,

    booking_date DATE,
    travel_date DATE,

    departure_time VARCHAR(30),
    arrival_time VARCHAR(30),

    duration_minutes INTEGER NOT NULL,
    stops INTEGER NOT NULL,

    fare NUMERIC(10,2) NOT NULL,

    CONSTRAINT fk_observation_source
        FOREIGN KEY (source_id)
        REFERENCES data_sources(source_id),

    CONSTRAINT fk_observation_airline
        FOREIGN KEY (airline_id)
        REFERENCES airlines(airline_id),

    CONSTRAINT fk_observation_route
        FOREIGN KEY (route_id)
        REFERENCES routes(route_id),

    CONSTRAINT fk_observation_flight
        FOREIGN KEY (flight_id)
        REFERENCES flights(flight_id),

    CONSTRAINT fk_observation_cabin
        FOREIGN KEY (cabin_class_id)
        REFERENCES cabin_classes(cabin_class_id),

    CONSTRAINT fk_observation_booking_window
        FOREIGN KEY (booking_window_id)
        REFERENCES booking_windows(booking_window_id),

    CONSTRAINT positive_fare
        CHECK (fare > 0),

    CONSTRAINT positive_duration
        CHECK (duration_minutes > 0),

    CONSTRAINT valid_stops
        CHECK (stops >= 0)
);


-- ------------------------------------------------------------
-- 8. INDEX VALUES
-- ------------------------------------------------------------

CREATE TABLE index_values (
    index_id BIGSERIAL PRIMARY KEY,

    index_date DATE NOT NULL,

    index_type VARCHAR(30) NOT NULL,
    index_period VARCHAR(20),

    route_id INTEGER,
    airline_id INTEGER,
    booking_window_id INTEGER,

    index_value NUMERIC(12,4) NOT NULL,
    percentage_change NUMERIC(10,4),

    CONSTRAINT fk_index_route
        FOREIGN KEY (route_id)
        REFERENCES routes(route_id),

    CONSTRAINT fk_index_airline
        FOREIGN KEY (airline_id)
        REFERENCES airlines(airline_id),

    CONSTRAINT fk_index_booking_window
        FOREIGN KEY (booking_window_id)
        REFERENCES booking_windows(booking_window_id),

    CONSTRAINT valid_index_value
        CHECK (index_value >= 0),

    CONSTRAINT valid_index_type
        CHECK (
            index_type IN (
                'daily',
                'weekly',
                'monthly',
                'route',
                'airline',
                'booking_window'
            )
        )
);


CREATE INDEX idx_index_values_date
    ON index_values(index_date);

CREATE INDEX idx_index_values_type
    ON index_values(index_type);

CREATE INDEX idx_index_values_route
    ON index_values(route_id);

CREATE INDEX idx_index_values_airline
    ON index_values(airline_id);

CREATE INDEX idx_index_values_booking_window
    ON index_values(booking_window_id);



CREATE TABLE index_contributions (
    contribution_id BIGSERIAL PRIMARY KEY,

    index_date DATE NOT NULL,

    dimension_type VARCHAR(30) NOT NULL,
    dimension_value VARCHAR(100) NOT NULL,

    contribution NUMERIC(12,4) NOT NULL
);

CREATE INDEX idx_contributions_date
    ON index_contributions(index_date);

CREATE INDEX idx_contributions_dimension
    ON index_contributions(dimension_type);




-- ============================================================
-- INITIAL MASTER DATA
-- ============================================================

-- Booking windows used by our project
INSERT INTO booking_windows (days_before_departure)
VALUES
    (1),
    (7),
    (15),
    (21),
    (30),
    (45),
    (60);


-- ============================================================
-- INDEXES FOR FREQUENT QUERIES
-- ============================================================

CREATE INDEX idx_observations_source
    ON fare_observations(source_id);

CREATE INDEX idx_observations_airline
    ON fare_observations(airline_id);

CREATE INDEX idx_observations_route
    ON fare_observations(route_id);

CREATE INDEX idx_observations_flight
    ON fare_observations(flight_id);

CREATE INDEX idx_observations_cabin
    ON fare_observations(cabin_class_id);

CREATE INDEX idx_observations_booking_window
    ON fare_observations(booking_window_id);

CREATE INDEX idx_observations_travel_date
    ON fare_observations(travel_date);

CREATE INDEX idx_observations_booking_date
    ON fare_observations(booking_date);

CREATE INDEX idx_index_values_date
    ON index_values(index_date);

CREATE INDEX idx_index_values_route
    ON index_values(route_id);

CREATE INDEX idx_index_values_airline
    ON index_values(airline_id);

CREATE INDEX idx_index_values_booking_window
    ON index_values(booking_window_id);