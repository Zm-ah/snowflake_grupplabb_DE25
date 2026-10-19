-- One row per airport, identified by IATA code
SELECT
    iata_code AS airport_key,
    iata_code,
    icao_code,
    airport_name,
    city,
    airport_usage,
    runways,
    passengers_2023
FROM {{ ref('stg_airports') }}
WHERE iata_code IS NOT NULL
  AND iata_code != ''
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY iata_code
    ORDER BY airport_name
) = 1

