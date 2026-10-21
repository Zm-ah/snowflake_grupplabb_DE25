# Entry point for Dagster: collects everything Dagster should know about.
from pathlib import Path

from dagster import AssetExecutionContext, Definitions
from dagster_dbt import DbtCliResource, DbtProject, dbt_assets

# Path to the dbt project folder (flight_dbt) in the repo root
DBT_PROJECT_DIR = Path(__file__).resolve().parent.parent / "flight_dbt"

# profiles.yml lives in ~/.dbt (outside the repo, so the password stays private)
dbt_project = DbtProject(
    project_dir=DBT_PROJECT_DIR,
    profiles_dir=Path.home() / ".dbt",
)
# Builds the dbt manifest automatically when running "dagster dev"
dbt_project.prepare_if_dev()


@dbt_assets(manifest=dbt_project.manifest_path)
def flight_dbt_assets(context: AssetExecutionContext, dbt: DbtCliResource):
    """Run dbt build and report each model and test to Dagster."""
    yield from dbt.cli(["build"], context=context).stream()


defs = Definitions(
    assets=[flight_dbt_assets],
    resources={"dbt": DbtCliResource(project_dir=dbt_project)},
)