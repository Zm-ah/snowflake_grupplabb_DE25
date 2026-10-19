{% macro clean_code(column_name) %}
    UPPER(TRIM({{ column_name }}))
{% endmacro %}