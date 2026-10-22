# Entry point for Dagster: collects everything Dagster should know about.
import os
import sys
from pathlib import Path
from dagster import AssetSelection, ScheduleDefinition, define_asset_job

import dlt
from dagster import (
    AssetExecutionContext,
    AssetSpec,
    Definitions,
    MaterializeResult,
    multi_asset,
)
from dagster_dbt import DbtCliResource, DbtProject, dbt_assets

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DBT_PROJECT_DIR = PROJECT_ROOT / "flight_dbt"

# The dlt code lives in dlt_code/ (not a Python package), so add it to the import path
sys.path.append(str(PROJECT_ROOT / "dlt_code"))
from swedavia_flights import flights_resource  # noqa: E402
from wikipedia_tables import airlines_resource, airports_resource  # noqa: E402

# Locally, profiles.yml lives in ~/.dbt (outside the repo, so the password stays
# private). In Docker, DBT_PROFILES_DIR points to a profiles.yml that reads its
# secrets from environment variables.
dbt_project = DbtProject(
    project_dir=DBT_PROJECT_DIR,
    profiles_dir=Path(os.getenv("DBT_PROFILES_DIR", Path.home() / ".dbt")),
)
dbt_project.prepare_if_dev()

# The raw tables dlt creates in Snowflake (the same keys dbt reads from)
RAW_TABLES = ["flights", "airports", "airlines"]


@multi_asset(specs=[AssetSpec(key=["raw", table]) for table in RAW_TABLES])
def dlt_raw_tables(context: AssetExecutionContext):
    """Run the dlt pipeline: Swedavia flights and Wikipedia tables to Snowflake."""
    pipeline = dlt.pipeline(
        pipeline_name="swedavia_flights",
        destination="snowflake",
        dataset_name="staging",
    )
    load_info = pipeline.run(
        [flights_resource(), airports_resource(), airlines_resource()]
    )
    context.log.info(str(load_info))
    for table in RAW_TABLES:
        yield MaterializeResult(asset_key=["raw", table])


@dbt_assets(manifest=dbt_project.manifest_path)
def flight_dbt_assets(context: AssetExecutionContext, dbt: DbtCliResource):
    """Run dbt build and report each model and test to Dagster."""
    yield from dbt.cli(["build"], context=context).stream()


# Runs the whole chain (dlt, then dbt) every night, after midnight Swedish time,
# so yesterday's flights have their actual times
nightly_job = define_asset_job("nightly_pipeline", selection=AssetSelection.all())

nightly_schedule = ScheduleDefinition(
    job=nightly_job,
    cron_schedule="0 3 * * *",
    execution_timezone="Europe/Stockholm",
)

defs = Definitions(
    assets=[dlt_raw_tables, flight_dbt_assets],
    resources={"dbt": DbtCliResource(project_dir=dbt_project)},
    jobs=[nightly_job],
    schedules=[nightly_schedule],
)