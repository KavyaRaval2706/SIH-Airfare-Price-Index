# Calculation Team — Setup & Handoff

## 1. What you will receive

I will give you:

1. **GitHub repository URL**
2. **`airfare_project.dump`** through WhatsApp

The dump contains the PostgreSQL database with the current airfare data.

---

# 2. Clone the repository

Open **Command Prompt** and run:

```cmd
git clone <REPOSITORY_URL>
```

Then:

```cmd
cd SIH-Airfare-Price-Index
```

---

# 3. Install PostgreSQL

Download PostgreSQL for Windows from:

https://www.postgresql.org/download/windows/

During installation:

* Keep the default PostgreSQL port: `5432`
* Create a password for the `postgres` user
* Keep **pgAdmin 4** selected
* Complete the installation

PostgreSQL's official downloads provide Windows installers.

---

# 4. Check PostgreSQL installation

Open a **new Command Prompt** and run:

```cmd
psql --version
```

Then:

```cmd
pg_restore --version
```

You should get PostgreSQL version information.

If Windows says that `pg_restore` is not recognized, run:

```cmd
"C:\Program Files\PostgreSQL\18\bin\pg_restore.exe" --version
```

---

# 5. Create the database

Run:

```cmd
psql -U postgres -c "CREATE DATABASE airfare_project;"
```

Enter your PostgreSQL password.

---

# 6. Restore the database dump

Suppose you saved the dump in your Downloads folder.

Run:

```cmd
pg_restore -U postgres -d airfare_project "C:\Users\YOUR_USERNAME\Downloads\airfare_project.dump"
```

Replace:

```text
YOUR_USERNAME
```

with your Windows username.

Example:

```cmd
pg_restore -U postgres -d airfare_project "C:\Users\Rahul\Downloads\airfare_project.dump"
```

The dump is in PostgreSQL custom format, so `pg_restore` is the correct tool for restoring it.

---

# 7. Verify the database

Run:

```cmd
psql -U postgres -d airfare_project -c "\dt"
```

You should see:

```text
data_sources
airlines
routes
flights
cabin_classes
booking_windows
fare_observations
index_values
```

Check the number of observations:

```cmd
psql -U postgres -d airfare_project -c "SELECT COUNT(*) FROM fare_observations;"
```

Expected result:

```text
745519
```

---

# 8. Install Python packages

From the project folder, run:

```cmd
pip install pandas numpy psycopg[binary] python-dotenv
```

---

# 9. Create `.env`

Inside the project root, create a file named:

```text
.env
```

Put:

```text
DB_HOST=localhost
DB_PORT=5432
DB_NAME=airfare_project
DB_USER=postgres
DB_PASSWORD=YOUR_POSTGRES_PASSWORD
```

Replace:

```text
YOUR_POSTGRES_PASSWORD
```

with the password you created during PostgreSQL installation.

**Do not commit `.env` to GitHub.**

---

# 10. Test Python → PostgreSQL connection

Run the existing connection test:

```cmd
python Import\test_postgresql.py
```

Expected output:

```text
PostgreSQL connection successful!
```

---

# 11. Calculation input

Use the PostgreSQL table:

```text
fare_observations
```

The main fields required for calculation include:

```text
observation_id
airline_id
route_id
cabin_class_id
booking_window_id
booking_date
travel_date
fare
```


---

# 12. Calculation outputs

Generate these CSV files:

```text
daily_airfare_index.csv
route_wise_airfare_index.csv
airline_wise_airfare_index.csv
booking_window_index.csv
index_contributions.csv
```


# 13. What you have to provide me at the end

Give me:

### Calculation code

```text
index_engine.py
```

### Output files

```text
daily_airfare_index.csv
route_wise_airfare_index.csv
airline_wise_airfare_index.csv
booking_window_index.csv
index_contributions.csv
```




# Final handoff

Your final calculation folder should contain approximately:

```text
Calculation/
├── index_engine.py
├── daily_airfare_index.csv
├── route_wise_airfare_index.csv
├── airline_wise_airfare_index.csv
├── booking_window_index.csv
└── index_contributions.csv
```

Send these files. Make folder of Calculation and keep all your files in it as shown above.
