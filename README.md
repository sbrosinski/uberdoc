# Uberdoc

Uberdoc is a wrapper script for [pandoc](http://johnmacfarlane.net/pandoc/) which provides a build system to turn a number of e.g. markdown files into large documents.

I use it to write technical documents. Default output is HTML. Optionally it generates a nicely formatted PDF using LaTex.

The provided default templates are just a starting point. These should be personalized for custom, e.g. client specific documents.

Tested on MacOS and Windows.

## Directory Layout

    src                     --> contains the documents chapters
        chapter1
            img             --> optional image files for this chapter
            chapter1.md     --> markdown content for this chapter
        chapter2
            chapter2.md
        toc.txt             --> reference of all chapters and their order

    styles                  --> optional css styles etc.
    templates               --> html and latex templates (for PDF conversion)
    
    out                     --> your doc ends up here

## Commands

    $ ./uberdoc.py create
    Creating dir structure and sample chapters ...

    $ ./uberdoc.py build
    Check environment ...
    Cleaning ...
    Parse toc ...
    Copy dependencies ...
    Generating document ...
    Done ...

    Options:
    --help : usage info
    --pdf : create a PDF in addition to HTML
    --verbose : show what params pandoc was called with
    
    $ ./uberdoc.py clean

## Configuration

You may change *uberdoc.cfg* as follows:

    [DEFAULT]

    # dir for chapter content
    src_dir = src 

    # build output dir
    out_dir = out

    # chapter image folder name
    img_dir = img

    # dir for css styles
    style_dir = style

    # file name of table of contents file
    toc_filename =toc.txt

    # base name for resulting document
    doc_filename = concept

    # extension for chapter files, default is Markdown
    input_ext = .md

    # pandoc command, needs to be in path
    pandoc_cmd = pandoc

    # pandoc conversion options for html
    pandoc_options_html = -s --template=../templates/default.html

    # pandoc conversions options for pdf
    pandoc_options_pdf =  -s --template=../templates/default.tex --toc --number-sections -V geometry:"top=2cm, bottom=3cm, left=2.5cm, right=2cm"

*Now start writing and stop messing with your tools!*
