# SIH Airfare Price Index

This project is being developed for the **Smart India Hackathon (SIH)**.

The project aims to develop a **Real-time Airfare Price Index for India** using airfare data collected from airline and online travel sources.

## Project Structure

```text
SIH-Airfare-Price-Index/
│
├── data/
│   └── airfare_clean.csv
│
├── database/
│   └── create_tables.sql
│
├── validation/
│   └── validation.py
│
├── cleaning/
│   └── cleaning.py
│
├── import/
│   └── import_to_mysql.py
│
└── README.md
```

## Dataset

The current prototype uses a cleaned airfare dataset containing **94 observations**.

The dataset contains information such as:

- Airline
- Route
- Flight
- Source
- Travel date
- Booking window
- Fare type
- Base fare
- Taxes
- Mandatory charges
- Total fare

## Setup Instructions

### 1. Install Required Python Packages

Open the terminal and run:

```bash
pip install pandas mysql-connector-python
```

### 2. Create the Database

Open **MySQL Workbench**.

Run the SQL script:

```text
database/create_tables.sql
```

This creates the `airfare_project` database and its five tables.

### 3. Import the Dataset

Run:

```bash
python import/import_to_mysql.py
```

The program will ask for your MySQL password.

Enter **your own MySQL password**.

### 4. Verify the Database

Open MySQL Workbench and run:

```sql
USE airfare_project;

SHOW TABLES;
```

To check the number of observations:

```sql
SELECT COUNT(*) AS total_observations
FROM fare_observations;
```

The current prototype should contain **94 observations**.

## Important

Do not upload MySQL passwords, API keys, or other credentials to GitHub.

Each team member should use their own local MySQL credentials.

The MySQL database is stored locally on each team member's computer. The GitHub repository contains the files required to recreate the database.