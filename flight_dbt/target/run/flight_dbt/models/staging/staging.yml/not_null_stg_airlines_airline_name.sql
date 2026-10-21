
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select airline_name
from FLIGHT_DB.ANALYTICS_stg.stg_airlines
where airline_name is null



  
  
      
    ) dbt_internal_test