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

### Next steps
- [ ] `sources.yml` (the tables in `STAGING`)
- [ ] Staging models
- [ ] Dimensions and fact table
- [ ] Tests and documentation
- [ ] Streamlit dashboard
- [ ] Dagster
- [ ] Docker and Azure (VG)
