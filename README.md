# snowflake_grupplabb_DE25
# dlt: Swedavia to Snowflake

Fetches arrivals and departures from Swedavia's FlightInfo API and loads them into Snowflake with dlt.

| Part | Value |
|---|---|
| Airports | ARN, BMA, GOT, MMX, LLA, UME, OSD, VBY, RNB, KRN |
| Period | Today and the two days before (3 days) |
| Directions | Arrivals and departures |
| API calls per run | 60 (10 airports × 3 days × 2 directions) |
| Snowflake database | `FLIGHT_DB` |
| Schema | `STAGING` |
| Warehouse | `SWEDAVIA_WH` |
| Role | `SWEDAVIA_DLT_ROLE` |
| User that loads data | `SWEDAVIA_LOADER` |
| Main table | `FLIGHT_DB.STAGING.FLIGHTS` (about 3,163 flights after the first run) |

## Run it

```bash
uv sync
uv run python dlt_code/load_api_swedavia.py
```

Run from the root folder, so dlt can find `.dlt/secrets.toml`.

## Secrets (never in git)

- `.env` holds `SWEDAVIA_API_KEY`.
- `.dlt/secrets.toml` holds the Snowflake login for `SWEDAVIA_LOADER`.

Both are ignored by git. Each person creates their own copy and asks the account owner for the password.

## Good to know

- Swedavia needs the header `Accept: application/json`, otherwise it returns `400`.
- The pipeline uses `merge`, so it can be run repeatedly without duplicate flights.
- `merge` needs the role to have `CREATE SCHEMA` on `FLIGHT_DB`.
- The SQL setup files in `worksheet_snowflake/` are run once per Snowflake account, in VS Code. 



## Project status and completed steps (14/oktober)

### 1. Environment setup
```bash
uv sync                      # installs all packages from pyproject.toml / uv.lock
```
Create a `.env` file in the root folder (never pushed to GitHub):
```
SWEDAVIA_API_KEY=your_key_here
```

### 2. Snowflake (SQL files in `worksheet_snowflake/`)
- Database `FLIGHT_DB`, schema `STAGING` (raw data from dlt) and warehouse `SWEDAVIA_WH`
- Role and user for dlt: `SWEDAVIA_DLT_ROLE`
- Role and user for dbt: `SWEDAVIA_DBT_ROLE` / `SWEDAVIA_TRANSFORMER`
  - `setup_dbt_users.sql` creates the role and the user (the password is a placeholder, set your own)
  - `grants_dbt_role.sql` gives dbt read access to the raw data and the right to create its own schemas

### 3. dlt: load data into Snowflake
- Swedavia FlightInfo (arrivals + departures, 10 airports, 3 days)
- Wikipedia (airports and airlines)
```bash
uv run python dlt_code/load_api_swedavia.py
```

### 4. Data model
- Dimensional model drawn in dbdiagram: `data_model.dbml`

### 5. dbt
```bash
uv add dbt-core dbt-snowflake      # install dbt
uv run dbt init flight_dbt         # create the dbt project
cd flight_dbt
uv run dbt debug                   # test the connection to Snowflake
```
The login lives in `~/.dbt/profiles.yml` (outside the repo, each person has their own):
```yaml
flight_dbt:
  target: dev
  outputs:
    dev:
      type: snowflake
      account: <ACCOUNT_IDENTIFIER>
      user: SWEDAVIA_TRANSFORMER
      password: <PASSWORD>
      role: SWEDAVIA_DBT_ROLE
      database: FLIGHT_DB
      warehouse: SWEDAVIA_WH
      schema: ANALYTICS
      threads: 1
```
Status: dbt is connected to Snowflake (`dbt debug`: All checks passed).

## Project status and completed steps (21/oktober)

Everything from the 14/oktober status above is still valid. Since then the whole dbt chain has been built and the dashboard has started to take shape.

### 6. dbt: staging models
Built in `flight_dbt/models/`, reading the raw tables in `STAGING`:
- `stg_flights`
- `stg_airlines`
- `stg_airports`

### 7. dbt: dimensions and fact table
Built in the schema `ANALYTICS_MARTS`:
- `dim_date`
- `dim_airline` (65 rows)
- `dim_airport` (52 rows)
- `fct_flights`

```bash
cd flight_dbt
uv run dbt run                # builds all models
uv run dbt test               # runs all tests
```
Status: the whole chain runs and `dbt test` passes (PASS=9).

### 8. Streamlit dashboard
Pages: home, Airports, Airlines and Time trends. All pages read from the marts in Snowflake.
```bash
uv run streamlit run <path to the main Streamlit file>
```

### Known limitation: run the pipeline after midnight
The API gives scheduled times first and actual times later. If the pipeline runs early in the day, flights that have not taken off yet only have a scheduled time, so the numbers for that day are incomplete. Because of this we run the pipeline after midnight and only show complete days in the dashboard.

### Next steps
- [x] `sources.yml` (the tables in `STAGING`)
- [x] Staging models
- [x] Dimensions and fact table
- [x] Tests
- [ ] Documentation (`schema.yml` descriptions)
- [ ] Streamlit dashboard: final polish, only complete days, same numbers on all pages
- [ ] Dagster
- [ ] Docker and Azure (VG)
 