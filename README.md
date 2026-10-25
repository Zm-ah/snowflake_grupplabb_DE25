# snowflake_grupplabb_DE25
# dlt: Swedavia to Snowflake

Fetches arrivals and departures from Swedavia's FlightInfo API and loads them into Snowflake with dlt.

| Part | Value |
|---|---|
| Airports | ARN, BMA, GOT, MMX, LLA, UME, OSD, VBY, RNB, KRN |
| Period | Yesterday and the two days before (3 days) |
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

### 9. Dagster: orchestration
Dagster runs the whole chain in the right order: first dlt (raw tables in `STAGING`), then dbt (staging models, dimensions and the fact table). The code is in `dagster_project/definitions.py`.
 
What is defined there:
- dlt assets: `raw / flights`, `raw / airports`, `raw / airlines`
- dbt assets: all models in `flight_dbt` (`dbt build`, so models and tests)
- a nightly job and schedule that run everything at 03:00 (Europe/Stockholm)
```bash
uv sync                                                  # installs Dagster with the other packages
uv run dagster dev -f dagster_project/definitions.py     # starts Dagster
```
Open `http://localhost:3000`, go to **Lineage** and click **Materialize all** to run the whole pipeline by hand. Go to **Automation** to turn the nightly schedule on or off.
 
Dagster needs the same setup as the earlier steps: `.env` (Swedavia key), `.dlt/secrets.toml` (Snowflake login for dlt) and `~/.dbt/profiles.yml` (Snowflake login for dbt).
 
Note: the schedule only runs while Dagster is running, so on a laptop the computer must be on at 03:00. Running Dagster in Docker on Azure (see next steps) solves this.
 
### Known limitation: run the pipeline after midnight
The API gives scheduled times first and actual times later. If the pipeline runs early in the day, flights that have not taken off yet only have a scheduled time, so the numbers for that day are incomplete. The nightly schedule runs after midnight, and the dashboard only shows complete days (today is left out).
 
 ## Run the pipeline with Dagster

Dagster runs the whole pipeline in the right order: dlt loads the raw data, then dbt builds the models, and the dbt tests run as asset checks.

**Before you start** (these files are never committed)

| File | Content |
|------|---------|
| `.env` | `SWEDAVIA_API_KEY` |
| `.dlt/secrets.toml` | Snowflake credentials for dlt |
| `~/.dbt/profiles.yml` | Snowflake connection for dbt |

**Start Dagster** from the project root:

```bash
uv run dagster dev -f dagster_project/definitions.py
```

Wait for `Serving dagster-webserver on http://127.0.0.1:3000`, then open <http://127.0.0.1:3000>.

| Where in Dagster | What you do |
|------------------|-------------|
| Assets | See the lineage (dlt -> dbt). Select all and click **Materialize** to run everything manually |
| Automation | The schedule that runs the pipeline every night after midnight |

> The schedule only runs while Dagster is running.
> If you see `Could not reach user code server`, an old process is still running. Run `pkill -f dagster` and start again.

## Streamlit dashboard

The dashboard only reads the mart tables in Snowflake (`FCT_FLIGHTS`, `DIM_AIRLINE`, `DIM_AIRPORT`, `DIM_DATE`). It does not load any data.

```bash
uv run streamlit run streamlit_app/home.py
```

| Page | File | Shows |
|------|------|-------|
| Home | `streamlit_app/home.py` | Project overview |
| Airlines | `streamlit_app/pages/1_Airlines.py` | Share of delayed flights per airline |
| Airports | `streamlit_app/pages/2_Airports.py` | Delay statistics per airport |
| Time trends | `streamlit_app/pages/3_Time_trends.py` | Delays over time |

**How the numbers are counted**

- Delayed = more than 15 minutes late.
- Only flights that have operated are counted.
- Only complete days are shown (today is excluded, because its flights only have scheduled times).
- Median delay is used instead of the average, because a few extreme delays would distort the average.

**Shared code**

| File | Purpose |
|------|---------|
| `streamlit_app/db.py` | Snowflake connection, `run_query` and the date filter `LAST_3_DAYS` |
| `streamlit_app/styles.py` | Shared chart and table helpers |
| `streamlit_app/.streamlit/config.toml` | The theme. Colors are defined only here and read by `styles.py` |
| `streamlit_app/.streamlit/secrets.toml` | Credentials. Ignored by git, never commit it |

## Docker

The dashboard has its own Dockerfile in `streamlit_app/`. Run the image locally:

```bash
docker run --rm -p 8501:8501 --env-file .env.docker flight-streamlit
```

Then open <http://localhost:8501>.

- `.env.docker` holds the Snowflake credentials for the container and is never committed.
- An image is a snapshot of the code. After changing the code, rebuild the image before running or deploying it again.