-- Select and rename columns, standardize codes, remove airlines without a name
SELECT DISTINCT
    {{ clean_code('IATA') }} AS iata_code,
    {{ clean_code('ICAO') }} AS icao_code,
    TRIM(AIRLINE) AS airline_name,
    TRIM(CALL_SIGN) AS call_sign,
    TRIM(COUNTRY) AS country,
    TRIM(COMMENTS) AS comments
FROM {{ source('raw', 'airlines') }}
WHERE
    AIRLINE IS NOT NULL
    AND TRIM(AIRLINE) != ''
