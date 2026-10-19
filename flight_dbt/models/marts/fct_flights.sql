-- One row per flight, airport, direction and date, with delay measures
WITH flights AS (
    SELECT
        MD5(CONCAT_WS('|', flight_id, airport, direction, flight_date)) AS flight_key,
        flight_id,
        airport AS airport_key,
        airline_iata AS airline_key,
        direction,
        TRY_TO_DATE(flight_date) AS flight_date,
        callsign,
        departure_airport,
        arrival_airport,
        flight_status,
        scheduled_utc,
        estimated_utc,
        actual_utc,
        -- Delay in minutes: actual time minus scheduled time
        ROUND(DATEDIFF('second', scheduled_utc, actual_utc) / 60, 1) AS delay_minutes
    FROM {{ ref('stg_flights') }}
)

SELECT
    *,
    -- Cancelled flights have status Deleted
    (flight_status = 'Deleted') AS is_cancelled,
    -- Delayed means more than 15 minutes late; no actual time means not delayed
    COALESCE(delay_minutes > 15, FALSE) AS is_delayed
FROM flights