
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select flight_key
from FLIGHT_DB.ANALYTICS_marts.fct_flights
where flight_key is null



  
  
      
    ) dbt_internal_test