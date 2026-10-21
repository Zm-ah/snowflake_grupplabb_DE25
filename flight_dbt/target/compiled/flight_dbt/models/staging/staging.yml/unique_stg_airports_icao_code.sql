
    
    

select
    icao_code as unique_field,
    count(*) as n_records

from FLIGHT_DB.ANALYTICS_stg.stg_airports
where icao_code is not null
group by icao_code
having count(*) > 1


