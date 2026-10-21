
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    flight_key as unique_field,
    count(*) as n_records

from FLIGHT_DB.ANALYTICS_marts.fct_flights
where flight_key is not null
group by flight_key
having count(*) > 1



  
  
      
    ) dbt_internal_test