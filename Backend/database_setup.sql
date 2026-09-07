CREATE DATABASE IF NOT EXISTS airfare_index;
USE airfare_index;

CREATE TABLE IF NOT EXISTS daily_airfare_index (
    id INT AUTO_INCREMENT PRIMARY KEY,
    observation_date DATE NOT NULL,
    airfare_index DECIMAL(10,4),
    available_cells INT,
    coverage_percent DECIMAL(10,4),
    quality_status VARCHAR(50),
    week VARCHAR(30),
    month VARCHAR(7)
);

CREATE TABLE IF NOT EXISTS weekly_airfare_index (
    id INT AUTO_INCREMENT PRIMARY KEY,
    week VARCHAR(30) NOT NULL,
    airfare_index DECIMAL(10,4),
    week_on_week_change_percent DECIMAL(10,4)
);

CREATE TABLE IF NOT EXISTS monthly_airfare_index (
    id INT AUTO_INCREMENT PRIMARY KEY,
    month VARCHAR(7) NOT NULL,
    airfare_index DECIMAL(10,4),
    month_on_month_change_percent DECIMAL(10,4)
);

CREATE TABLE IF NOT EXISTS route_wise_airfare_index (
    id INT AUTO_INCREMENT PRIMARY KEY,
    observation_date DATE NOT NULL,
    route VARCHAR(20) NOT NULL,
    route_airfare_index DECIMAL(10,4)
);
INSERT INTO weekly_airfare_index
(week, airfare_index, week_on_week_change_percent)
VALUES
('2026-07-27/2026-08-02', 98.94988563110834, NULL),
('2026-08-03/2026-08-09', 100.85711544634938, 1.9274704594923087),
('2026-08-10/2026-08-16', 107.70901944263619, 6.793674363938806),
('2026-08-17/2026-08-23', 107.63551269852292, -0.06824567199075204);

INSERT INTO monthly_airfare_index
(month, airfare_index, month_on_month_change_percent)
VALUES
('2026-08', 103.50543288312788, NULL);