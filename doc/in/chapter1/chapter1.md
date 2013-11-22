% Uberdoc
% Stephan Brosinski
%

# Uberdoc

Uberdoc is a wrapper script for [Pandoc](http://johnmacfarlane.net/pandoc/) which provides a build system to turn a number of e.g. markdown files into large documents.

I use it to write technical documents. Default output is HTML. Optionally it generates a nicely formatted PDF using LaTex.

The provided default templates are just a starting point. These should be personalized for custom, e.g. client specific documents.

## Directory Layout

Uberdoc uses the following directory layout for your document.

    in                      --> contains the document's chapters
        chapter1
            img             --> optional image files for this chapter
            chapter1.md     --> markdown content for this chapter
        chapter2
            chapter2.md
        toc.txt             --> reference of all chapters and their order

    styles                  --> optional css styles etc.
    templates               --> optional html and latex templates (for PDF conversion)

    out                     --> your doc ends up here

## Usage

Initializing a new dir for uberdoc, this creates a sample document and config file

    $ udoc init
    Copying default config file ...
    Creating dir structure and sample chapters ...

Create a git repo for current document, provide an initial gitignore and commit

    $ udoc git
    Initializing git repo in current dir and adding files ...
    git init
    git add .gitignore
    git add in
    git add uberdoc.cfg
    git commit -m "setup uberdoc document"

Create document, use -p for PDF output in addition to HTML

    $ udoc build
    Check environment ...
    Cleaning ...
    Parse toc ...
    Copy dependencies ...
    Generating document ...
    Done ...

Open new document in browser or PDF viewer

    $ udoc show

If you want to customize the default HTML/Latex templates or CSS styles,
run this command to create a copy of the default templates for your document. Then edit the files
in ./templates or ./style.

    $ udoc customize
    Creating templates ...
    Creating styles ...

This scans the document's toc.txt table of contents file, shows which chapter directories exist in
in the document dir, creates new chapter dirs and offers (with --delete) to remove chapters which are
not in the table of contents anymore:

    $ udoc outline
    Exists: chapter1 -> ./in/chapter1/chapter1.md
    Exists: chapter2 -> ./in/chapter2/chapter2.md
    Exists: chapter3 -> ./in/chapter3/chapter3.md
    Creating: chapter4 -> ./in/chapter4/chapter4.md

    $ udoc outline --delete
    Exists: chapter1 -> ./in/chapter1/chapter1.md
    Exists: chapter3 -> ./in/chapter3/chapter3.md
    Exists: chapter4 -> ./in/chapter4/chapter4.md
    Missing: chapter2 -> ./in/chapter2/chapter2.md
    Remove chapter2? (y/N):

You can place a # in front of a TOC entry to disable a chapter or a ! to force Uberdoc to only consider this chapter.
This way you can for example only build a subset of your document, or, using the outline command easily remove certain
chapters.

If Pandoc or Uberdoc throw errors, run this command to check if your document setup is okay.

    $ udoc check
    Loading config: uberdoc.cfg
    Config settings:
      doc_dir = .
      in_dir = in
      out_dir = out
      img_dir = img
      style_dir = style
      toc_filename = toc.txt
      doc_filename = concept
      input_ext = .md
      pandoc_cmd = pandoc
      pandoc_options_html = -s --default-image-extension=png --template=../templates/default.html
      pandoc_options_pdf = -s --default-image-extension=pdf --template=../templates/default.tex --toc --number-sections -V "geometry:top=2cm, bottom=3cm, left=2.5cm, right=2cm"
    Document version: 2013-10-10 (dc89484)
    Environment setup ok.

## Tips

* Uberdoc creates a VERSION variable containing the documents current git hash which can be used in your HTML or Latex templates
* You can place a # in front of a TOC entry to disable a chapter or a ! to force Uberdoc to only consider this chapter
* By using --default-image-extension as a Pandoc config option Pandoc will for example use PNGs for HTML and PDFs for PDF documents without you having to change the image links in your markdown, see the sample doc

## Requirements

* Python 2.6, 2.8. or 3 on MacOS or Linux (Windows should work, but no guarantees)
* a recent version of [Pandoc](http://johnmacfarlane.net/pandoc/) (newer than 1.9)
* git
* LaTex if you want to create PDF documents, please take a look at [Pandoc's instructions](http://johnmacfarlane.net/pandoc/installing.html)
* Depending on the LaTex template use, you may have to use the LaTex distribution's package manager to install additional LaTex packages.

## Installation

The easiest way would be [pip](https://pypi.python.org/pypi/pip):

    pip install uberdoc

You can also clone this repository and run

    python setup.py install

## Configuration

You may change *uberdoc.cfg* as follows:

    [DEFAULT]

    # dir for chapter content
    in_dir = src

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

## Contributing

Uberdoc uses [nose](http://nose.readthedocs.org/en/latest/) for testing and [tox](http://testrun.org/tox/latest/) to run tests for different Python versions.

Just run either

    $ nosetests

    $ tox

### Ideas for improvement

* A markdown pre-processor which supports plugins so you can easly extends the existing markdown syntax or change document content when generating the document
* Support for epub generation, so large documents can be better read on mobile devices
* Diff-View, generate a version of the document showing the differences to a former version

*Now start writing and stop messing with your tools!*

