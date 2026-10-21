
  create or replace   view FLIGHT_DB.ANALYTICS_stg.stg_airports
  
  
  
  
  as (
    -- Select and rename columns and standardize codes
SELECT DISTINCT
    TRIM(CITY_SERVED) AS city,
    
    UPPER(TRIM(ICAO))
 AS icao_code,
    TRIM(AIRPORT_NAME) AS airport_name,
    
    UPPER(TRIM(IATA))
 AS iata_code,
    TRIM(USAGE) AS airport_usage,
    RUNWAYS AS runways,
    PASSENGERS_2023 AS passengers_2023
FROM FLIGHT_DB.STAGING.airports
  );

