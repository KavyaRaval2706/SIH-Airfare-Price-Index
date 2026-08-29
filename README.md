# SIH Airfare Price Index

This project is being developed for the **Smart India Hackathon (SIH)**.

The project aims to develop a **Real-time Airfare Price Index for India** using airfare data collected from airline and online travel sources.

## Project Structure

```text
SIH-Airfare-Price-Index/
│
├── airfare_clean.csv
├── create_tables.sql
├── validation.py
├── cleaning.py
├── import_to_mysql.py
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

## Getting Started

### 1. Clone the Repository

First, make sure you have **Git installed** on your computer.

Open **VS Code** and open the terminal.

Run:

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

Replace `YOUR_GITHUB_REPOSITORY_URL` with the URL of this GitHub repository.

For example:

```bash
git clone https://github.com/USERNAME/SIH-Airfare-Price-Index.git
```

After cloning, move into the project folder:

```bash
cd SIH-Airfare-Price-Index
```

The project files should now be available on your computer.

### 2. Install Required Python Packages

Open the terminal inside the project folder and run:

```bash
pip install pandas mysql-connector-python
```

### 3. Create the Database

Open **MySQL Workbench**.

Open the file:

```text
create_tables.sql
```

Run the complete SQL script.

This creates the `airfare_project` database and its five tables.

### 4. Import the Dataset

Make sure `airfare_clean.csv` and `import_to_mysql.py` are in the same folder.

Run:

```bash
python import_to_mysql.py
```

The program will ask for your MySQL password.

Enter **your own MySQL password**.

Do not use another team member's password.

### 5. Verify the Database

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

## Database

The MySQL database is named:

**airfare_project**

It contains five tables:

1. **airlines** — Stores airline information
2. **routes** — Stores origin and destination information
3. **sources** — Stores the source of the airfare data
4. **flights** — Stores flight information
5. **fare_observations** — Stores the actual airfare observations

### Database Relationships

```text
airlines ──────┐
               ↓
             flights
               ↓
       fare_observations

routes ────────↑

sources ─────────────→ fare_observations
```

## Files

| File | Purpose |
|---|---|
| `airfare_clean.csv` | Cleaned prototype airfare dataset |
| `create_tables.sql` | Creates the MySQL database and tables |
| `validation.py` | Validates the dataset |
| `cleaning.py` | Cleans the dataset |
| `import_to_mysql.py` | Imports the cleaned dataset into MySQL |
| `README.md` | Project documentation |

## Security

Do not upload:

- MySQL passwords
- API keys
- Other private credentials

The import script asks for the MySQL password when it runs, so passwords do not need to be stored in the code.

Each team member should use their **own local MySQL credentials**.

The MySQL database is stored locally on each team member's computer. The GitHub repository contains the files required to recreate the database.

## Working with GitHub

After cloning the repository, do not delete or modify another team member's work without discussing it with the team.

Before starting new work, get the latest version of the project:

```bash
git pull
```

After completing your work:

```bash
git add .
git commit -m "Describe your changes"
git push
```

Always run `git pull` before starting work to make sure you have the latest version.

## Project Status

### Completed

- Prototype dataset created
- Dataset validated
- Dataset cleaned
- Relational database designed
- MySQL tables created
- CSV imported into MySQL
- Database verified
- GitHub repository created

