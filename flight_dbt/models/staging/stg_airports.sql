SELECT DISTINCT
    CITY_SERVED AS city,
    ICAO AS icao_code,
    AIRPORT_NAME AS airport_name,
    IATA AS iata_code,
    USAGE AS airport_usage,
    RUNWAYS AS runways,
    PASSENGERS_2023 AS passengers_2023
FROM {{ source('raw', 'airports') }}
