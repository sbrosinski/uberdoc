# Extending the Markdown Syntax

Uberdoc uses a templating engine to allow user to extend the markdown syntax used in its chapter files.

## Predefined Variables

The following variables are provided by Uberdoc and can be used in markdown files by e.g. adding

{% raw %}
    {{udoc.doc_version}}
{% endraw %}

Variable | Value
---------|---------
{% for key in udoc %}{{ key }}|{{ udoc[key] }}
{% endfor %}

## Custom Variables

Variable | Value
---------|---------
{% for key in conf %}{{ key }}|{{ conf[key] }}
{% endfor %}

## Macros

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

## Filters

Or using filters:

{% raw %}
    {% filter upper %}
    This text becomes uppercase
    {% endfilter %}
{% endraw %}
{% filter upper %}
This text becomes uppercase
{% endfilter %}

## Includes

Or including other markdown files:

{% raw %}
    {% include 'templating/some.md' %}
{% endraw %}
{% include 'templating/some.md' %}