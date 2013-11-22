# Extending the Markdown Syntax

Uberdoc uses a templating engine to allow user to extend the markdown syntax used in its chapter files.

## Predefined Variables

The following variables are provided by Uberdoc and can be used in markdown files by e.g. adding


    {{udoc.doc_version}}


Variable | Value
---------|---------
md_file|templating/templating.md
version|1.2.2
doc_version|2013-11-22 (fe88fa1)


## Custom Variables

Variable | Value
---------|---------
doc_dir|.
b|c


## Macros

Defining a macro in your markdown document:


    {% macro todo(description) -%}
    > *TODO:* {{description}}
    {%- endmacro %}




Calling the TODO macro:


    {{todo('this needs to be rewritten!')}}


results in:

> *TODO:* this needs to be rewritten!

## Filters

Or using filters:


    {% filter upper %}
    This text becomes uppercase
    {% endfilter %}


THIS TEXT BECOMES UPPERCASE


## Includes

Or including other markdown files:


    {% include 'templating/some.md' %}

**This is a seperate markdown file *some.md* being included by the Templating Demo chapter**