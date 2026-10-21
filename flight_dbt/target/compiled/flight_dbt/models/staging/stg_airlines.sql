-- Select and rename columns, standardize codes, remove airlines without a name
SELECT DISTINCT
    
    UPPER(TRIM(IATA))
 AS iata_code,
    
    UPPER(TRIM(ICAO))
 AS icao_code,
    TRIM(AIRLINE) AS airline_name,
    TRIM(CALL_SIGN) AS call_sign,
    TRIM(COUNTRY) AS country,
    TRIM(COMMENTS) AS comments
FROM FLIGHT_DB.STAGING.airlines
WHERE
    AIRLINE IS NOT NULL
    AND TRIM(AIRLINE) != ''