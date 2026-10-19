

-- Välja och döpa om kolumner, kombinerat ankomst- och avgångstider och ta bort identiska rader i resultatet

SELECT DISTINCT
    FLIGHT_ID AS flight_id,
    AIRPORT AS airport,
    DIRECTION AS direction,
    FLIGHT_DATE AS flight_date,
    FLIGHT_LEG_IDENTIFIERCALLSIGN AS callsign,
    FLIGHT_LEG_IDENTIFIERDEPARTURE_AIRPORT_IATA AS departure_airport,
    FLIGHT_LEG_IDENTIFIERARRIVAL_AIRPORT_IATA AS arrival_airport,
    UPPER(TRIM(AIRLINE_OPERATORIATA)) AS airline_iata,
    UPPER(TRIM(AIRLINE_OPERATORICAO)) AS airline_icao,
    TRIM(AIRLINE_OPERATORNAME) AS airline_name,
    LOCATION_AND_STATUSFLIGHT_LEG_STATUS_ENGLISH AS flight_status,

    COALESCE(
        ARRIVAL_TIMESCHEDULED_UTC,
        DEPARTURE_TIMESCHEDULED_UTC
    ) AS scheduled_utc,

    COALESCE(
        ARRIVAL_TIMEESTIMATED_UTC,
        DEPARTURE_TIMEESTIMATED_UTC
    ) AS estimated_utc,

    COALESCE(
        ARRIVAL_TIMEACTUAL_UTC,
        DEPARTURE_TIME__ACTUAL_UTC
    ) AS actual_utc

FROM {{ source('raw', 'flights') }}