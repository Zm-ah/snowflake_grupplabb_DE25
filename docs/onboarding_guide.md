
## Getting started (for teammates)

1. `git pull` on `main`.
2. `uv sync` gives you the same environment as everyone else.
3. Create your own `.env` and `.dlt/secrets.toml` (they are not in the repo).
4. Ask the Snowflake account owner for the password to `SWEDAVIA_LOADER`. Never share it through git or an open chat.
5. Do not re-run the SQL files in `worksheet_snowflake/`. They are run once per account.
6. Run `uv run python dlt_code/load_api_swedavia.py` from the root folder.