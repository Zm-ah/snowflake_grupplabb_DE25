
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select airport_name
from FLIGHT_DB.ANALYTICS_stg.stg_airports
where airport_name is null



  
  
      
    ) dbt_internal_test