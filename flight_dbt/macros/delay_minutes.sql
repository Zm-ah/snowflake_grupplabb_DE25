-- Return the delay in minutes between a scheduled and an actual timestamp
{% macro delay_minutes(scheduled, actual) %}
    ROUND(DATEDIFF('second', {{ scheduled }}, {{ actual }}) / 60, 1)
{% endmacro %}

