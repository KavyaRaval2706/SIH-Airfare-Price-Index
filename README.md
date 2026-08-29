# SIH Airfare Price Index

This project is being developed for Smart India Hackathon (SIH).

The project aims to develop a Real-time Airfare Price Index for India using airfare data collected from airline and online travel sources.

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

Dataset

The current prototype uses a cleaned airfare dataset containing 94 observations.

The dataset contains information such as:

Airline
Route
Flight
Source
Travel date
Booking window
Fare type
Base fare
Taxes
Mandatory charges
Total fare
Setup Instructions
1. Install required Python packages

Open the terminal and run:

pip install pandas mysql-connector-python
2. Create the database

Open MySQL Workbench.

Run the SQL script:

database/create_tables.sql

This creates the airfare_project database and its five tables.

3. Import the dataset

Run:

python import/import_to_mysql.py

The program will ask for your MySQL password.

Enter your own MySQL password.

4. Verify the database

Open MySQL Workbench and run:

USE airfare_project;

SHOW TABLES;

To check the number of observations:

SELECT COUNT(*) AS total_observations
FROM fare_observations;

The current prototype should contain 94 observations.

Important

Do not upload MySQL passwords, API keys, or other credentials to GitHub.

Each team member should use their own local MySQL credentials.

The MySQL database is stored locally on each team member's computer. The GitHub repository contains the files required to recreate the database.


