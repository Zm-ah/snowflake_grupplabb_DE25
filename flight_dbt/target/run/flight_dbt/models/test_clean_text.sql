
  create or replace   view FLIGHT_DB.ANALYTICS.test_clean_text
  
  
  
  
  as (
    SELECT
    
    UPPER(TRIM('  SWEDAVIA  '))
 AS airline_name,
    
    UPPER(TRIM('  ARN  '))
 AS airport_code,
    
    UPPER(TRIM(NULL))
 AS missing_value
  );

