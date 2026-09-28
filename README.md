# AeroIndex — Airfare Price Index for India

AeroIndex is a data-driven dashboard for measuring and monitoring changes in domestic airfare prices across India.

The project develops an **Airfare Price Index** designed to support analysis of airfare movements and future augmentation of consumer price statistics.

> **Note:** AeroIndex is an airfare index and analytics system. It is **not a flight booking system or a cheapest-ticket recommendation platform**.

## Project

**Smart India Hackathon — SIH26056**

**Problem:** Development of a Real-time Airfare Price Index for India through automated collection of airline and online travel data for augmentation of the Consumer Price Index (CPI).

## Key Features

* Current Airfare Price Index and percentage change
* Historical daily, weekly and monthly index trends
* Route-wise index analysis
* Airline-wise index analysis
* Booking-window analysis from **T+1 to T+50**
* Why Did the Index Change? — route, airline and booking-window attribution
* Historical data explorer
* PostgreSQL-based data storage
* REST APIs using FastAPI

## System Architecture

```text
Data Sources
     ↓
Source Adapters
     ↓
Common Data Model
     ↓
Validation & Deduplication
     ↓
Normalization
     ↓
Fare Index Calculation
     ↓
PostgreSQL
     ↓
FastAPI
     ↓
AeroIndex Dashboard
```

The production architecture is designed to support permitted airline APIs, NDC integrations, OTA APIs and other authorized data sources through source-specific adapters.

## Index Methodology

### Base Period

The first seven available days, **16-01-2023 to 22-01-2023**, are used as the base period with an index value of **100**.

### Daily Index

For each route and date:

1. Calculate the median airfare.
2. Compare it with the route's base-period median.
3. Calculate the price relative.
4. Aggregate route-level price relatives to obtain the daily index.

### Weekly & Monthly Index

Weekly and monthly indices are calculated from the corresponding daily index values.

### Booking Window

Airfares are analyzed separately for each booking window from **T+1 to T+50**, where T represents the travel date. T+1 is used as the reference booking window.

### Change Attribution

Index changes can be examined through contributions from:

* Routes
* Airlines
* Booking windows

## Technology Stack

| Component             | Technology           |
| --------------------- | -------------------- |
| Data Processing       | Python, Pandas       |
| Data Validation       | Python               |
| Database              | PostgreSQL           |
| Backend               | FastAPI              |
| Frontend              | React, Vite          |
| Visualization         | Recharts             |
| Database Connectivity | PostgreSQL / psycopg |
| Version Control       | Git, GitHub          |

## Project Structure

```text
SIH-Airfare-Price-Index/
│
├── Backend/
├── Frontend/
├── Calculation/
│   ├── index_engine.py
│   └── Output/
├── Cleaning/
├── Data/
│   ├── raw/
│   └── processed/
├── Database/
├── Import/
├── Normalization/
├── Validation/
├── .gitignore
└── README.md
```

Large datasets and database dumps are kept outside the Git repository.

## Prototype Data

The current prototype uses historical flight-fare data for development and demonstration.

**Source:** [Kaggle — Airfare ML: Predicting Flight Fares](https://www.kaggle.com/datasets/yashdharme36/airfare-ml-predicting-flight-fares)

Current prototype coverage:

* **Date:** 16-01-2023 to 06-03-2023
* **Airlines:** 9
* **Routes:** 42
* **Booking windows:** T+1 to T+50

For production deployment, the system is intended to use permitted airline, NDC, OTA/API or other authorized sources.

## Running the Project

### Backend

```bash
cd Backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend

```bash
cd Frontend
npm install
npm run dev
```

### Calculation

The index calculation engine is located at:

```text
Calculation/index_engine.py
```

Generated calculation outputs are stored in:

```text
Calculation/Output/
```

## Project Status

AeroIndex is currently a **working prototype** developed for Smart India Hackathon.

The architecture is designed to support expansion from prototype historical data to permitted real-time airfare data sources.
