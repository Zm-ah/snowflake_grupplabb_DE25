
    
    

select
    airline_key as unique_field,
    count(*) as n_records

from FLIGHT_DB.ANALYTICS_marts.dim_airline
where airline_key is not null
group by airline_key
having count(*) > 1


