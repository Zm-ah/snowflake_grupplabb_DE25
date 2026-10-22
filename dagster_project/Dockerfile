FROM python:3.13-slim

WORKDIR /app
RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY dagster_project ./dagster_project
COPY dlt_code ./dlt_code
COPY flight_dbt ./flight_dbt

ENV PATH="/app/.venv/bin:$PATH" \
    DBT_PROFILES_DIR=/app/dagster_project/dbt_profiles \
    DAGSTER_HOME=/app/dagster_home
RUN mkdir -p /app/dagster_home

EXPOSE 3000
CMD ["dagster", "dev", "-h", "0.0.0.0", "-p", "3000", "-f", "dagster_project/definitions.py"]