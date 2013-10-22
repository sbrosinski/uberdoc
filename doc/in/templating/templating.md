
# Templating Demo

Defining a macro in your markdown document:

{% raw %}
    {% macro todo(description) -%}
    > *TODO:* {{description}}
    {%- endmacro %}
{% endraw %}

{% macro todo(description) -%}
> *TODO:* {{description}}
{%- endmacro %}

Calling the TODO macro:

{% raw %}
    {{todo('this needs to be rewritten!')}}
{% endraw %}

results in:

{{todo('this needs to be rewritten!')}}

Or using filters:

{% raw %}
    {% filter upper %}
    This text becomes uppercase
    {% endfilter %}
{% endraw %}
{% filter upper %}
This text becomes uppercase
{% endfilter %}

Or including other markdown files:

{% raw %}
    {% include 'templating/some.md' %}
{% endraw %}
{% include 'templating/some.md' %}