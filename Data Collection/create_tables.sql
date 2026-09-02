CREATE DATABASE IF NOT EXISTS airfare_project;

USE airfare_project;

CREATE TABLE airlines (
    airline_id INT PRIMARY KEY AUTO_INCREMENT,
    airline_name VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE routes (
    route_id INT PRIMARY KEY AUTO_INCREMENT,
    origin CHAR(3) NOT NULL,
    destination CHAR(3) NOT NULL,
    UNIQUE(origin, destination)
);

CREATE TABLE sources (
    source_id INT PRIMARY KEY AUTO_INCREMENT,
    source_name VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE flights (
    flight_id INT PRIMARY KEY AUTO_INCREMENT,
    airline_id INT NOT NULL,
    route_id INT NOT NULL,
    flight_number VARCHAR(20) NOT NULL,

    FOREIGN KEY (airline_id)
        REFERENCES airlines(airline_id),

    FOREIGN KEY (route_id)
        REFERENCES routes(route_id)
);

CREATE TABLE fare_observations (
    observation_id VARCHAR(20) PRIMARY KEY,
    observation_date DATE NOT NULL,
    source_id INT NOT NULL,
    flight_id INT NOT NULL,
    travel_date DATE NOT NULL,
    departure_time TIME,
    stops INT,
    booking_window INT,
    fare_type VARCHAR(50),
    base_fare DECIMAL(10,2),
    taxes DECIMAL(10,2),
    mandatory_charges DECIMAL(10,2),
    total_fare DECIMAL(10,2),
    data_status VARCHAR(30),

    FOREIGN KEY (source_id)
        REFERENCES sources(source_id),

    FOREIGN KEY (flight_id)
        REFERENCES flights(flight_id)
);