
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select airport_key
from FLIGHT_DB.ANALYTICS_marts.dim_airport
where airport_key is null



  
  
      
    ) dbt_internal_test