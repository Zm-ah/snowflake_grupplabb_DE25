
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    airport_key as unique_field,
    count(*) as n_records

from FLIGHT_DB.ANALYTICS_marts.dim_airport
where airport_key is not null
group by airport_key
having count(*) > 1



  
  
      
    ) dbt_internal_test