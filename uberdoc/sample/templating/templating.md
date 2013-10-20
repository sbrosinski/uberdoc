# Templating Demo

Defining a macro in your markdown document:

{% macro todo(description) -%}
> *TODO:* {{description}}
{%- endmacro %}

Calling the TODO macro:

{{todo('this needs to be rewritten!')}}

Or using filters:

{% filter upper %}
This text becomes uppercase
{% endfilter %}

Or including other markdown files:

{% include 'templating/some.md' %}