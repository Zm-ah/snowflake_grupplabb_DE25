-- Select and rename columns and standardize codes
SELECT DISTINCT
    TRIM(CITY_SERVED) AS city,
    {{ clean_code('ICAO') }} AS icao_code,
    TRIM(AIRPORT_NAME) AS airport_name,
    {{ clean_code('IATA') }} AS iata_code,
    TRIM(USAGE) AS airport_usage,
    RUNWAYS AS runways,
    PASSENGERS_2023 AS passengers_2023
FROM {{ source('raw', 'airports') }}

