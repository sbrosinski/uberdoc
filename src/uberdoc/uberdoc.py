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
import pkg_resources
import datetime
from pkg_resources import resource_filename
from termcolor import colored, cprint

__author__ = "Stephan Brosinski"
__version__ = pkg_resources.require("uberdoc")[0].version

class Config:
    """Encapsulates config file access"""    
    def __init__(self, file_name):
        if not os.path.isfile(file_name):
            file_name = resource_filename(__name__, "uberdoc.cfg")    
        self.conf = ConfigParser.ConfigParser()
        self.conf.readfp(open(file_name))

    def __getattr__(self, name):    
        """Shortcut for accessing config options which are handled as
        Config class properties
        """
        return self.conf.get("DEFAULT", name) 

    def show(self):
        for key, value in self.conf.items("DEFAULT"):
            print "  " + key + " = " + value  


_conf = Config("uberdoc.cfg")

def cmd(cmdStr, verbose = False, cwd = '.', echo = False, env = {}):
    """Executes cmdStr as shell command in the working directory provided
    by cwd
    """

    if echo: print(cmdStr)

    cmd_env = dict(os.environ.items() + env.items())
    #cmd_env = os.environ

    if verbose: 
        print '-------- executing cmd -------------'
        print 'cmd: ' + cmdStr + '\n'
        print 'cwd: ' + cwd + '\n'
        print 'env: ' + str(cmd_env) + '\n'

    process = subprocess.Popen(shlex.split(cmdStr),
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               cwd = cwd,
                               env = cmd_env)

    (stdout, stderr) = process.communicate()

    if verbose and stdout: 
        print 'out: ' + stdout
        
    if process.returncode > 0:
        cprint(stderr, "red")
    
    if verbose:
        print '-------- done executing cmd --------'

    return (process.returncode, stdout, stderr)

def generate_file_list(toc_lines):
    """Uses the toc to generate chapter relative paths to the input files"""
    files = []
    for line in toc_lines:
        files.append(os.path.join(line, line + _conf.input_ext))  
    return files

def generate_doc(files):
    """Calls pandoc to generate html, and optionally PDF docs"""
    file_list =  " ".join(files)    
    out_file = os.path.join("..", _conf.out_dir, _conf.doc_filename)    
    
    # always build html doc
    build_cmd = " ".join([
        _conf.pandoc_cmd, 
        _conf.pandoc_options_html, 
        ' -V VERSION:"{0}" '.format(version()),
        file_list, 
        "-o", 
        out_file + ".html"])
    cmd(build_cmd, cwd = _conf.in_dir, verbose = _args.verbose)  

    # build pdf in addition, if required (takes a lot longer)
    if _args.pdf:
        build_cmd = " ".join([
            _conf.pandoc_cmd, 
            _conf.pandoc_options_pdf, 
            ' -V VERSION:"{0}" '.format(version()),
            ' --template=' + resource_filename(__name__, "templates/default.tex"),
            file_list,  
            "-o", 
            out_file + ".pdf"])
        cmd(build_cmd, cwd = _conf.in_dir, verbose = _args.verbose)  

def clean(recreate_out = False):
    """Recreates out_dir""" 
    if os.path.isdir(_conf.out_dir):
        shutil.rmtree(_conf.out_dir)
    if recreate_out:
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
    
        if os.path.isdir(os.path.join(_conf.in_dir, line, _conf.img_dir)):
            os.mkdir(os.path.join(_conf.out_dir, line))
      
            shutil.copytree(
                os.path.join(_conf.in_dir, line, _conf.img_dir), 
                os.path.join(_conf.out_dir, line, _conf.img_dir))


def read_toc():
    """Reads the toc file containing the chapter list."""
    with open(os.path.join(_conf.in_dir, _conf.toc_filename)) as f:
        lines = f.read().splitlines()
    return [line for line in lines if not line.startswith("#")]

def build():
    """Calls all steps of the doc build process"""
    print "Check environment ..."
    check_env(verbose = False)

    print "Cleaning ..."
    clean(recreate_out = True) 

    print "Parse toc ..."
    toc = read_toc()

    print "Copy dependencies ..."
    copy_dependencies(toc)

    print "Generating document ..."
    generate_doc(generate_file_list(toc))
    
    cprint("Done ...", "green")

def version():
    #uberdoc_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
    uberdoc_dir = "."
    env = {"GIT_WORK_TREE": uberdoc_dir, "GIT_DIR": os.path.join(uberdoc_dir, ".git")}
    
    returncode, version_str, error = cmd('git log -1 --format="%cd (%h)" --date=short', 
        cwd = uberdoc_dir,
        env = env) 

    if returncode > 0:
        cprint("Current dir is not a git repository.", "yellow")
        return datetime.datetime.now().strftime("%Y-%m-%d")
    else:
        return version_str

def git():
    """Turns the current dir into a git repo and adds default .gitignore"""
    print("Initializing git repo in current dir and adding files ...")
    cmd('git init', echo = True)
    shutil.copyfile(resource_filename(__name__, "default_gitignore"), ".gitignore")
    cmd('git add .gitignore', echo = True)
    cmd('git add in', echo = True)
    cmd('git add uberdoc.cfg', echo = True)
    cmd('git commit -m "setup uberdoc document"', echo = True)

def show():
    file_html = os.path.join(_conf.out_dir, _conf.doc_filename + ".html")
    file_pdf = os.path.join(_conf.out_dir, _conf.doc_filename + ".pdf")
    # on windows this should be
    #os.startfile(file_html)
    cmd("open " + file_html)
    if os.path.isfile(file_pdf):
        cmd("open " + file_pdf)

def init_doc():
    """Generates an example src dir structure, for new doc projects."""
    print "Copying default config file ..."
    shutil.copyfile(resource_filename(__name__, "uberdoc.cfg"), "uberdoc.cfg")

    print "Creating dir structure and sample chapters ..."
    src = _conf.in_dir
    os.mkdir(src)
    os.makedirs(os.path.join(src, "chapter1", "img"))
    os.makedirs(os.path.join(src, "chapter2", "img"))   
    with open(os.path.join(src, "toc.txt"), "w") as toc:
        toc.writelines(["chapter1\n", "chapter2\n"])
    with open(os.path.join(src, "chapter1", "chapter1.md"), "w") as chapter1:
        chapter1.write("# Chapter 1 \n")
        chapter1.write("A sample chapter. \n")
    with open(os.path.join(src, "chapter2", "chapter2.md"), "w") as chapter2:
        chapter2.write("# Chapter 2 \n")
        chapter2.write("A second sample chapter. \n")

def check_env(verbose = True):
    def exit_if(condition, msg):
        if condition:
            print >> sys.stderr, colored(msg, "red")
            sys.exit(1)

    if verbose:
        print("Uberdoc version: " + __version__)
        cprint("Config settings: ", "yellow")
        if not os.path.isfile("uberdoc.cfg"):
            print "No project specific config file. Using defaults."
        _conf.show()    
        print("Document version: " + version())

    exit_if(
        not distutils.spawn.find_executable(_conf.pandoc_cmd),
        "Error: Couldn't find pandoc in current path.")

    exit_if(
        not distutils.spawn.find_executable("git"),
        "Error: Couldn't find git in current path.") 

    exit_if(
        not os.path.isdir(_conf.in_dir),
        "Error: Couldn't find input folder. Was expecting folder: " + _conf.in_dir)

    toc_file_path = os.path.join(_conf.in_dir, _conf.toc_filename)
    exit_if(
        not os.path.isfile(toc_file_path),
        "Error: Couldn't find toc file. Was expecting: " + toc_file_path)

    if verbose: cprint("Environment setup ok.", "green")

def main():
    parser = argparse.ArgumentParser(
        description = "Wraps pandoc to create a writing environment for large documents.",
        epilog = "Now start writing and stop messing with your tools!")

    parser.add_argument("--version", action = "version", version = "Version " + __version__) 

    subparsers = parser.add_subparsers(help = "sub-command help")

    parser_clean = subparsers.add_parser("clean", help = "removes build artifacts")
    parser_clean.set_defaults(func = clean)

    parser_create = subparsers.add_parser(
        "init", 
        help = "inits the directory structure for a new document")
    parser_create.set_defaults(func = init_doc)

    parser_check = subparsers.add_parser(
        "check",
        help = "checks if your document environment is setup correctly")
    parser_check.set_defaults(func = check_env)

    parser_build = subparsers.add_parser(
        "build", 
        help = "generates the document")
    parser_build.add_argument(
        "-p", 
        "--pdf", 
        help = "also creates a PDF version", 
        action = "store_true")
    parser_build.add_argument(
        "-v", 
        "--verbose", 
        help = "gives more details on what is happening during conversion", 
        action = "store_true")
    parser_build.set_defaults(func = build)

    parser_git = subparsers.add_parser(
        "git", 
        help = "turns document dir into git repo")
    parser_git.set_defaults(func = git)

    parser_show = subparsers.add_parser(
        "show",
        help = "shows current document in browser")
    parser_show.set_defaults(func = show)

    global _args;
    _args = parser.parse_args()
    _args.func()


if __name__ == "__main__":
    main()