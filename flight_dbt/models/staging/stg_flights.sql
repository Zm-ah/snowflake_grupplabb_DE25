

-- Välja och döpa om kolumner, kombinerat ankomst- och avgångstider och ta bort identiska rader i resultatet

SELECT DISTINCT
    FLIGHT_ID AS flight_id,
    AIRPORT AS airport,
    DIRECTION AS direction,
    FLIGHT_DATE AS flight_date,
    FLIGHT_LEG_IDENTIFIER__CALLSIGN AS callsign,
    FLIGHT_LEG_IDENTIFIER__DEPARTURE_AIRPORT_IATA AS departure_airport,
    FLIGHT_LEG_IDENTIFIER__ARRIVAL_AIRPORT_IATA AS arrival_airport, 

    COALESCE(
        ARRIVAL_TIME__SCHEDULED_UTC,
        DEPARTURE_TIME__SCHEDULED_UTC
    ) AS scheduled_utc,

    COALESCE(
        ARRIVAL_TIME__ESTIMATED_UTC,
        DEPARTURE_TIME__ESTIMATED_UTC
    ) AS estimated_utc,

    COALESCE(
        ARRIVAL_TIME__ACTUAL_UTC,
        DEPARTURE_TIME__ACTUAL_UTC
    ) AS actual_utc

FROM {{ source('raw', 'flights') }}