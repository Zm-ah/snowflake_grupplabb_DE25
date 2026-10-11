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
