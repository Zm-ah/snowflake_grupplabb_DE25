
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select icao_code
from FLIGHT_DB.ANALYTICS_stg.stg_airports
where icao_code is null



  
  
      
    ) dbt_internal_test