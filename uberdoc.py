#!/usr/bin/env python

"""Wrapper script for pandoc. Useful for larger documents, since it breaks up
several e.g. markdown files into chapters and provides a build process to
generate html and pdf docs from them.
"""

import os
import argparse
import ConfigParser
import sys
import subprocess
import shlex
import shutil
import distutils.spawn

__author__ = 'Stephan Brosinski'
__version__ = '1.0'

class Config:
    """Encapsulates config file access"""    
    def __init__(self, file_name):
        if not os.path.isfile(file_name):
            print >> sys.stderr, 'Error: Could not find config file: ' + file_name 
            sys.exit(1)        
        self.conf = ConfigParser.ConfigParser()
        self.conf.readfp(open(file_name))

    def __getattr__(self, name):    
        """Shortcut for accessing config options which are handled as
        Config class properties
        """
        return self.conf.get('DEFAULT', name)  

_conf = Config('uberdoc.cfg')

def cmd(cmdStr, verbose = False, cwd = '.'):
    """Executes cmdStr as shell command in the working directory provided
    by cwd
    """
    if verbose: 
        print 'cmd: ' + cmdStr

    process = subprocess.Popen(shlex.split(cmdStr),
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               cwd = cwd)

    (stdout, stderr) = process.communicate()

    if verbose and stdout: 
        print 'cmd: ' + stdout
        
    if process.returncode > 0:
      print stderr
    
    return stdout

def generate_file_list(toc_lines):
    """Uses the toc to generate chapter relative paths to the input files"""
    files = []
    for line in toc_lines:
        files.append(os.path.join(line, line + _conf.input_ext))  
    return files

def generate_doc(files):
    """Calls pandoc to generate html, and optionally PDF docs"""
    file_list =  ' '.join(files)    
    out_file = os.path.join('..', _conf.out_dir, _conf.doc_filename)    
    
    # always build html doc
    build_cmd = ' '.join([
        _conf.pandoc_cmd, 
        _conf.pandoc_options_html, 
        ' -V VERSION:"{0}" '.format(version()),
        file_list, 
        '-o', 
        out_file + '.html'])
    cmd(build_cmd, cwd = _conf.src_dir, verbose = _args.verbose)  

    # build pdf in addition, if required (takes a lot longer)
    if _args.pdf:
        build_cmd = ' '.join([
            _conf.pandoc_cmd, 
            _conf.pandoc_options_pdf, 
            ' -V VERSION:"{0}" '.format(version()),
            file_list, 
            '-o', 
            out_file + '.pdf'])
        cmd(build_cmd, cwd = _conf.src_dir, verbose = _args.verbose)  

def clean():
    """Recreates out_dir""" 
    if os.path.isdir(_conf.out_dir):
        shutil.rmtree(_conf.out_dir)
    os.mkdir(_conf.out_dir)

def copy_dependencies(toc_lines):
    """Copies the contents of style_dir (e.g. css files) to out_dir.
    Chapters with images will have their images copied there as
    well, while preserving the chapter dir structure
    """
    if os.path.isdir(_conf.style_dir):
        shutil.copytree(
            _conf.style_dir, 
            os.path.join(_conf.out_dir, _conf.style_dir))
  
    for line in toc_lines:
    
        if os.path.isdir(os.path.join(_conf.src_dir, line, _conf.img_dir)):
            os.mkdir(os.path.join(_conf.out_dir, line))
      
            shutil.copytree(
                os.path.join(_conf.src_dir, line, _conf.img_dir), 
                os.path.join(_conf.out_dir, line, _conf.img_dir))


def read_toc():
    """Reads the toc file containing the chapter list."""
    with open(os.path.join(_conf.src_dir, _conf.toc_filename)) as f:
        lines = f.read().splitlines()
    return [line for line in lines if not line.startswith('#')]

def build():
    """Calls all steps of the doc build process"""
    print 'Check environment ...'
    check_env()

    print 'Cleaning ...'
    clean(); 

    print 'Parse toc ...'
    toc = read_toc()

    print 'Copy dependencies ...'
    copy_dependencies(toc)

    print 'Generating document ...'
    generate_doc(generate_file_list(toc))
    
    print 'Done ...'

def version():
    return cmd('git log -1 --format="%cd (%h)" --date=short') 

def create():
    """Generates an example src dir structure, for new doc projects."""
    print "Creating dir structure and sample chapters ..."
    src = _conf.src_dir
    os.mkdir(src)
    os.makedirs(os.path.join(src, 'chapter1', 'img'))
    os.makedirs(os.path.join(src, 'chapter2', 'img'))   
    with open(os.path.join(src, 'toc.txt'), 'w') as toc:
        toc.writelines(['chapter1\n', 'chapter2\n'])
    with open(os.path.join(src, 'chapter1', 'chapter1.md'), 'w') as chapter1:
        chapter1.write('# Chapter 1 \n')
        chapter1.write('A sample chapter. \n')
    with open(os.path.join(src, 'chapter2', 'chapter2.md'), 'w') as chapter2:
        chapter2.write('# Chapter 2 \n')
        chapter2.write('A second sample chapter. \n')

def check_env():
    def exit_if(condition, msg):
        if condition:
            print >> sys.stderr, msg
            sys.exit(1)

    exit_if(
        not distutils.spawn.find_executable(_conf.pandoc_cmd),
        "Error: Couldn't find pandoc in current path.")

    exit_if(
        not distutils.spawn.find_executable('git'),
        "Error: Couldn't find git in current path.") 

    exit_if(
        not os.path.isdir(_conf.src_dir),
        "Error: Couldn't find src folder.")

    exit_if(
        not os.path.isfile(os.path.join(_conf.src_dir, _conf.toc_filename)),
        "Error: Couldn't find toc file.")

def main():
    parser = argparse.ArgumentParser(
        description = 'Wraps pandoc to create a writing environment for large documents.',
        epilog = "Now start writing and stop messing with your tools!")

    subparsers = parser.add_subparsers(help = 'sub-command help')

    parser_create = subparsers.add_parser(
        'create', 
        help = 'creates the structure for a new document')
    
    parser_create.set_defaults(func = create)

    parser_build = subparsers.add_parser(
        'build', 
        help = 'generates the document')
    
    parser_build.add_argument(
        '-p', 
        '--pdf', 
        help = 'also creates a PDF version', 
        action = 'store_true')
    
    parser_build.add_argument(
        '-v', 
        '--verbose', 
        help = 'gives more details on what is happening during conversion', 
        action = 'store_true')
    
    parser_build.set_defaults(func = build)

    global _args;
    _args = parser.parse_args()
    _args.func()


if __name__ == "__main__":
    main()