USE ROLE SECURITYADMIN;
GRANT ROLE SWEDAVIA_DLT_ROLE TO ROLE SYSADMIN;

USE ROLE SYSADMIN;
USE WAREHOUSE SWEDAVIA_WH;
SHOW TABLES IN SCHEMA FLIGHT_DB.STAGING;


SELECT COUNT(*) AS antal_flyg
FROM FLIGHT_DB.STAGING.FLIGHTS;

SELECT airport, direction, COUNT(*) AS antal
FROM FLIGHT_DB.STAGING.FLIGHTS
GROUP BY airport, direction
ORDER BY airport, direction;


DESCRIBE TABLE FLIGHT_DB.STAGING.FLIGHTS;

SELECT *
FROM FLIGHT_DB.STAGING.FLIGHTS
LIMIT 5;



// show the tables in the staging schema
SHOW TABLES IN SCHEMA FLIGHT_DB.STAGING;
// show the tables in the dlt schema
SELECT COUNT(*) AS antal_flygplatser FROM FLIGHT_DB.STAGING.AIRPORTS;


SELECT COUNT(*) AS antal_flygbolag FROM FLIGHT_DB.STAGING.AIRLINES;


// loking for the flight status codes
SELECT
    location_and_status__flight_leg_status AS status_code,
    MIN(location_and_status__flight_leg_status_english) AS exempel_text,
    COUNT(*) AS antal
FROM FLIGHT_DB.STAGING.FLIGHTS
GROUP BY 1
ORDER BY antal DESC;

// loking for the delayed flights
SELECT
    flight_id,
    airport,
    flight_date,
    direction,
    airline_operator__name,
    COALESCE(arrival_time__scheduled_utc, departure_time__scheduled_utc) AS scheduled_utc,
    COALESCE(arrival_time__actual_utc, departure_time__actual_utc) AS actual_utc
FROM FLIGHT_DB.STAGING.FLIGHTS
WHERE location_and_status__flight_leg_status = 'DEL'
LIMIT 15; 
// show the number of deleted flights by airport and direction 
SELECT
    airport,
    direction,
    COUNT(*) AS antal_borttagna
FROM FLIGHT_DB.STAGING.FLIGHTS
WHERE location_and_status__flight_leg_status = 'DEL'
GROUP BY airport, direction
ORDER BY antal_borttagna DESC;