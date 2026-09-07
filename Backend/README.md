# Airfare Price Index — Frontend Integration & Backend Setup Guide

This guide explains how to clone the project, set up the database, import the calculated data, run the FastAPI backend, and connect the frontend to the backend APIs.

---

## 1. Clone the Repository

Open a terminal in the location where you want to store the project.

### Run:

```powershell
git clone <YOUR-GITHUB-REPOSITORY-URL>
```

Then enter the project folder:

### Run:

```powershell
cd SIH-Airfare-Price-Index
```

---

## 2. Project Structure

The important project folders are:

```text
SIH-Airfare-Price-Index/
│
├── Backend/
│   ├── main.py
│   ├── database.py
│   ├── database_setup.sql
│   ├── requirements.txt
│   └── README.md
│
├── Calculation/
│   ├── daily_airfare_index.csv
│   ├── weekly_airfare_index.csv
│   ├── monthly_airfare_index.csv
│   └── route_wise_airfare_index.csv
│
└── Data Collection/
    └── ...
```

For frontend integration, the main folders are:

* `Backend/` → FastAPI APIs
* `Calculation/` → calculated airfare-index CSV files

---

# 3. Set Up MySQL

Install **MySQL Server** and **MySQL Workbench** on your computer.

Open MySQL Workbench and connect to your local MySQL server.

---

# 4. Create the Database and Tables

Open the following file from the repository:

```text
Backend/database_setup.sql
```

Copy the SQL code into a MySQL Workbench SQL Editor.

Execute the complete script.

This creates the database:

```text
airfare_index
```

and the following tables:

```text
daily_airfare_index
weekly_airfare_index
monthly_airfare_index
route_wise_airfare_index
```

---

# 5. Import the CSV Files into MySQL

The calculated data is available in the `Calculation` folder.

```text
Calculation/
├── daily_airfare_index.csv
├── weekly_airfare_index.csv
├── monthly_airfare_index.csv
└── route_wise_airfare_index.csv
```

Each CSV should be imported into its corresponding MySQL table.

| CSV file                       | Destination table          |
| ------------------------------ | -------------------------- |
| `daily_airfare_index.csv`      | `daily_airfare_index`      |
| `weekly_airfare_index.csv`     | `weekly_airfare_index`     |
| `monthly_airfare_index.csv`    | `monthly_airfare_index`    |
| `route_wise_airfare_index.csv` | `route_wise_airfare_index` |

MySQL Workbench provides a **Table Data Import Wizard** that supports CSV files and allows the destination table and column mapping to be configured.

### 5.1 Open the Database

In MySQL Workbench:

1. Open your MySQL connection.
2. In the **SCHEMAS** panel, find:

```text
airfare_index
```

3. Expand:

```text
airfare_index → Tables
```

You should see:

```text
daily_airfare_index
weekly_airfare_index
monthly_airfare_index
route_wise_airfare_index
```

---

### 5.2 Import `daily_airfare_index.csv`

Right-click:

```text
daily_airfare_index
```

Select:

```text
Table Data Import Wizard
```

Then:

1. Select the file:

```text
Calculation/daily_airfare_index.csv
```

2. Click **Next**.
3. Select the destination table:

```text
daily_airfare_index
```

4. Check that the CSV columns are mapped to the correct table columns.
5. Continue through the wizard.
6. Click **Next/Import** to start the import.
7. Wait for the import to finish.

MySQL Workbench's wizard supports CSV configuration including separators, encoding, column selection, and column/type mapping.

---

### 5.3 Import `weekly_airfare_index.csv`

Right-click:

```text
weekly_airfare_index
```

Select:

```text
Table Data Import Wizard
```

Select:

```text
Calculation/weekly_airfare_index.csv
```

Set the destination table to:

```text
weekly_airfare_index
```

Check the column mapping and complete the import.

---

### 5.4 Import `monthly_airfare_index.csv`

Right-click:

```text
monthly_airfare_index
```

Select:

```text
Table Data Import Wizard
```

Select:

```text
Calculation/monthly_airfare_index.csv
```

Set the destination table to:

```text
monthly_airfare_index
```

Check the column mapping and complete the import.

---

### 5.5 Import `route_wise_airfare_index.csv`

Right-click:

```text
route_wise_airfare_index
```

Select:

```text
Table Data Import Wizard
```

Select:

```text
Calculation/route_wise_airfare_index.csv
```

Set the destination table to:

```text
route_wise_airfare_index
```

Check the column mapping and complete the import.

---

### 5.6 Verify the Imported Data

After importing all four CSV files, run:

```sql
USE airfare_index;

SELECT * FROM daily_airfare_index;
SELECT * FROM weekly_airfare_index;
SELECT * FROM monthly_airfare_index;
SELECT * FROM route_wise_airfare_index;
```

You can also check the number of records:

```sql
SELECT COUNT(*) FROM daily_airfare_index;
SELECT COUNT(*) FROM weekly_airfare_index;
SELECT COUNT(*) FROM monthly_airfare_index;
SELECT COUNT(*) FROM route_wise_airfare_index;
```

---

# 6. Configure the Database Connection

Open:

```text
Backend/database.py
```

Configure the MySQL connection using the credentials of **your own computer**.

The connection should point to:

```text
Host: localhost
Database: airfare_index
```

Use your own MySQL username and password.

Do not use another team member's database password.

---

# 7. Create a Python Virtual Environment

Open a terminal inside the `Backend` folder.

### Run:

```powershell
python -m venv .venv
```

Activate the virtual environment.

### Run:

```powershell
.venv\Scripts\activate
```

After activation, the terminal should show something similar to:

```text
(.venv) PS C:\...\SIH-Airfare-Price-Index\Backend>
```

---

# 8. Install Backend Dependencies

Make sure the virtual environment is activated.

### Run:

```powershell
pip install -r requirements.txt
```

The required Python packages are listed in:

```text
Backend/requirements.txt
```

---

# 9. Start the FastAPI Backend

Make sure you are inside the `Backend` directory.

### Run:

```powershell
python -m uvicorn main:app --reload
```

If the server starts successfully, you should see something similar to:

```text
Uvicorn running on http://127.0.0.1:8000
```

Keep this terminal running while using the frontend.

---

# 10. Open the API Documentation

Open your browser and go to:

```text
http://127.0.0.1:8000/docs
```

FastAPI automatically provides interactive Swagger documentation at `/docs`. You can use it to view and test the available API endpoints.

You can also open:

```text
http://127.0.0.1:8000/redoc
```

---

# 11. Frontend → Backend Connection

The frontend should **not connect directly to MySQL**.

The architecture is:

```text
Frontend
    │
    │ HTTP Requests
    ▼
FastAPI Backend
    │
    │ SQLAlchemy / PyMySQL
    ▼
MySQL Database
```

The frontend communicates only with the FastAPI API.

---

# 12. Backend Base URL

When running locally, the backend base URL is:

```text
http://127.0.0.1:8000
```

The frontend should append the required API endpoint to this base URL.

For example:

```text
http://127.0.0.1:8000/<endpoint>
```

The exact endpoints available in the current backend can be viewed at:

```text
http://127.0.0.1:8000/docs
```

---

# 13. Example Frontend API Request

JavaScript example:

```javascript
fetch("http://127.0.0.1:8000/<ENDPOINT>")
  .then(response => response.json())
  .then(data => {
    console.log(data);
  });
```

Replace:

```text
<ENDPOINT>
```

with the actual endpoint shown in the FastAPI documentation.

---

# 14. Using the API Data

The frontend can use the API responses to create:

* Airfare index cards
* Daily index charts
* Weekly index charts
* Monthly index charts
* Route-wise charts
* Data tables
* Trend indicators
* Dashboard statistics

The exact JSON response format can be checked using the `/docs` page.

---

# 15. If Frontend and Backend Run on Different Ports

For example:

```text
Frontend:
http://localhost:3000

Backend:
http://127.0.0.1:8000
```

The backend may require CORS configuration to allow requests from the frontend.

If CORS is already configured in `main.py`, no additional configuration is required.

---

# 16. Quick Start

For a fresh setup, follow these steps.

### Clone

```powershell
git clone <YOUR-GITHUB-REPOSITORY-URL>
cd SIH-Airfare-Price-Index
```

### Database

Open:

```text
Backend/database_setup.sql
```

Run the SQL script in MySQL Workbench.

### Import CSV files

Import:

```text
Calculation/daily_airfare_index.csv
Calculation/weekly_airfare_index.csv
Calculation/monthly_airfare_index.csv
Calculation/route_wise_airfare_index.csv
```

into their corresponding tables using the **Table Data Import Wizard**.

### Backend setup

```powershell
cd Backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### Start backend

```powershell
python -m uvicorn main:app --reload
```

### Open API documentation

```text
http://127.0.0.1:8000/docs
```

---

# Important Notes

* The frontend does **not** connect directly to MySQL.
* The FastAPI backend handles database communication.
* Each developer should use their own local MySQL credentials.
* The calculation CSV files provide the current prototype data.
* The `/docs` page is the reference for the available API endpoints.
* Do not commit passwords or other credentials to the repository.
