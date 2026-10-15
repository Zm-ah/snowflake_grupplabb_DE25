SELECT DISTINCT
    *
FROM {{ source('raw', 'airlines') }}