import dlt
from swedavia_flights import flights_resource
from wikipedia_tables import airlines_resource, airports_resource


def run_pipeline():
    pipeline = dlt.pipeline(
        pipeline_name="swedavia_flights",
        destination="snowflake",
        dataset_name="staging",
    )

    load_info = pipeline.run(
        [flights_resource(), airports_resource(), airlines_resource()]
    )
    print(load_info)


if __name__ == "__main__":
    run_pipeline()