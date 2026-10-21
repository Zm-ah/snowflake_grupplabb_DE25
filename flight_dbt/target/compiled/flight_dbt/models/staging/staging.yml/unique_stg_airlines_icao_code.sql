
    
    

select
    icao_code as unique_field,
    count(*) as n_records

from (select * from FLIGHT_DB.ANALYTICS_stg.stg_airlines where icao_code is not null and trim(icao_code) != '') dbt_subquery
where icao_code is not null
group by icao_code
having count(*) > 1


