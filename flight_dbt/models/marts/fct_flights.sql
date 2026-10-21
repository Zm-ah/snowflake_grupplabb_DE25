
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
        -- Group statuses such as 'Landed 17:01' or 'Estimated 12:55' into a few categories
        CASE
            WHEN flight_status LIKE 'Landed%' THEN 'Landed'
            WHEN flight_status LIKE 'Estimated%' THEN 'Estimated'
            WHEN flight_status LIKE 'Delayed%' THEN 'Delayed'
            ELSE flight_status
        END AS status_group,
        scheduled_utc,
        estimated_utc,
        actual_utc,
        -- Delay in minutes: actual time minus scheduled time
        ROUND(DATEDIFF('second', scheduled_utc, actual_utc) / 60, 1) AS delay_minutes
    FROM {{ ref('stg_flights') }}
)

SELECT
    *,
    -- Cancelled: the flight was cancelled
    (status_group = 'Cancelled') AS is_cancelled,
    -- Deleted: removed from the schedule, never flown, excluded from statistics
    (status_group = 'Deleted') AS is_deleted,
    -- Only flights with an actual time can be judged on punctuality
    (actual_utc IS NOT NULL) AS has_actual_time,
    -- Delayed means more than 15 minutes late
    COALESCE(delay_minutes > 15, FALSE) AS is_delayed
FROM flights  