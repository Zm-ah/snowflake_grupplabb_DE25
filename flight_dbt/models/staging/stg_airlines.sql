SELECT DISTINCT
    IATA AS iata_code,
    ICAO AS icao_code,
    AIRLINE AS airline_name,
    CALL_SIGN AS call_sign,
    COUNTRY AS country,
    COMMENTS AS comments
FROM {{ source('raw', 'airlines') }}
