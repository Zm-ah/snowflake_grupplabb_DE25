-- One row per airline that operates flights in our data
WITH flight_airlines AS (
    -- Airlines as reported by Swedavia
    SELECT DISTINCT
        airline_iata,
        airline_icao,
        airline_name
    FROM {{ ref('stg_flights') }}
    WHERE airline_iata IS NOT NULL
      AND airline_iata != ''
),

one_per_iata AS (
    -- Guarantee a unique key: keep one row per IATA code
    SELECT *
    FROM flight_airlines
    QUALIFY ROW_NUMBER() OVER (
        PARTITION BY airline_iata
        ORDER BY airline_name
    ) = 1
),

wiki_airlines AS (
    -- Wikipedia data, deduplicated on ICAO code
    SELECT
        icao_code,
        call_sign,
        country
    FROM {{ ref('stg_airlines') }}
    WHERE icao_code IS NOT NULL
      AND icao_code != ''
    QUALIFY ROW_NUMBER() OVER (
        PARTITION BY icao_code
        ORDER BY airline_name
    ) = 1
)

SELECT
    f.airline_iata AS airline_key,
    f.airline_iata,
    f.airline_icao,
    f.airline_name,
    w.call_sign,
    w.country
FROM one_per_iata AS f
LEFT JOIN wiki_airlines AS w
    ON f.airline_icao = w.icao_code