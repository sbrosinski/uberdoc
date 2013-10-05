#!/usr/bin/env python

"""Wrapper script for pandoc. Useful for larger documents, since it breaks up
several e.g. markdown files into chapters and provides a build process to
generate html and pdf docs from them.
"""
from __future__ import print_function
import os
import argparse
import sys
import subprocess
import shlex
import shutil
import distutils.spawn
import pkg_resources
import datetime
from pkg_resources import resource_filename


if sys.version_info[0] > 2:
    from configparser import ConfigParser   
    from .termcolor import colored, cprint
else:
    from ConfigParser import ConfigParser    
    from termcolor import colored, cprint

__author__ = "Stephan Brosinski"
#__version__ = pkg_resources.require("uberdoc")[0].version
__version__ = "1"

class Config:
    """Encapsulates config file access"""    
    def __init__(self, file_name):
        if not os.path.isfile(file_name):
            file_name = resource_filename(__name__, "uberdoc.cfg") 
            if not os.path.isfile(file_name):
                raise Exception("Can't find config file: " + file_name + " " + os.path.dirname(os.path.abspath(__file__)) + " " + os.getcwd())
           
        print("Loading config: " + file_name)
        self.conf = ConfigParser()
        self.conf.readfp(open(file_name))
    
    #@staticmethod
    #def create_from(config, defaultvals = {}):
    #    newconfig = Config()
    #    for key, value in defaultvals.items():
    #        newconfig[key] = value
    #    for key, value in config.items():
    #        newconfig[key] = value 
    #    return newconfig

    def __getitem__(self, key):    
        """Shortcut for accessing config options which are handled as
        Config class properties
        """
        return self.conf.get("DEFAULT", key) 

    def __setitem__(self, key, value):
        self.conf.set("DEFAULT", key, value)

    def show(self):
        for key, value in self.conf.items("DEFAULT"):
            print("  " + key + " = " + value)

    def items(self):
        return self.conf.items("DEFAULT")




#_conf = Config("uberdoc.cfg")

class Uberdoc:

    def __init__(self, conf):
        #self.conf = Config.create_from(conf)
        self.conf = conf
        self.out_dir = self.prefix_path(self.conf["out_dir"])
        self.in_dir = self.prefix_path(self.conf["in_dir"])
        self.style_dir = self.prefix_path(self.conf["style_dir"])


    def cmd(self, cmdStr, verbose = False, cwd = '.', echo = False, env = []):
        """Executes cmdStr as shell command in the working directory provided
        by cwd
        """

        if echo: print(cmdStr)

        for key, value in env:
            os.environ[key] = value            

        cmd_env = os.environ
        #cmd_env = os.environ

        if verbose: 
            print('-------- executing cmd -------------')
            print('cmd: ' + cmdStr + '\n')
            print('cwd: ' + cwd + '\n')
            print('env: ' + str(cmd_env) + '\n')

        process = subprocess.Popen(shlex.split(cmdStr),
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   cwd = cwd,
                                   env = cmd_env)

        (stdout, stderr) = process.communicate()

        if verbose and stdout: 
            print('out: ' + stdout)
            
        if process.returncode > 0:
            cprint(stderr, "red")
        
        if verbose:
            print('-------- done executing cmd --------')

        return (process.returncode, stdout.decode('utf-8'), stderr.decode('utf-8'))

    def generate_file_list(self, toc_lines):
        """Uses the toc to generate chapter relative paths to the input files"""
        files = []
        for line in toc_lines:
            files.append(os.path.join(line, line + self.conf["input_ext"]))  
        return files

    def generate_doc(self, files, pdf = False, verbose = False):
        """Calls pandoc to generate html, and optionally PDF docs"""
        file_list =  " ".join(files)    


        out_file = os.path.join("..", self.conf["out_dir"], self.conf["doc_filename"])    
        
        # always build html doc
        build_cmd = " ".join([
            self.conf["pandoc_cmd"], 
            self.conf["pandoc_options_html"], 
            ' -V VERSION:"{0}" '.format(self.version()),
            file_list, 
            "-o", 
            out_file + ".html"])
        self.cmd(build_cmd, cwd = self.in_dir, verbose = verbose)  

        # build pdf in addition, if required (takes a lot longer)
        if pdf:
            build_cmd = " ".join([
            self.conf["pandoc_cmd"], 
            self.conf["pandoc_options_pdf"], 
                ' -V VERSION:"{0}" '.format(self.version()),
                ' --template=' + resource_filename(__name__, "templates/default.tex"),
                file_list,  
                "-o", 
                out_file + ".pdf"])
            self.cmd(build_cmd, cwd = self.in_dir, verbose = verbose)  

    def clean(self, recreate_out = False):
        """Recreates out_dir""" 
        print("removing " + self.out_dir)
        if os.path.isdir(self.out_dir):
            shutil.rmtree(self.out_dir)
            print("removed")
        if recreate_out:
            os.mkdir(self.out_dir)

    def copy_dependencies(self, toc_lines):
        """Copies the contents of style_dir (e.g. css files) to out_dir.
        Chapters with images will have their images copied there as
        well, while preserving the chapter dir structure
        """
        if os.path.isdir(self.style_dir):
            shutil.copytree(
                self.style_dir, 
                os.path.join(self.out_dir, self.style_dir))
      
        for line in toc_lines:
            img_dir = self.conf["img_dir"]
            if os.path.isdir(os.path.join(self.in_dir, line, img_dir)):
                os.mkdir(os.path.join(self.out_dir, line))
          
                shutil.copytree(
                    os.path.join(self.in_dir, line, img_dir), 
                    os.path.join(self.out_dir, line, img_dir))


    def read_toc(self):
        """Reads the toc file containing the chapter list."""
        with open(os.path.join(self.in_dir, self.conf["toc_filename"])) as f:
            lines = f.read().splitlines()
        return [line for line in lines if not line.startswith("#")]

    def build(self, pdf = False):
        """Calls all steps of the doc build process"""  
        print("Check environment ...")
        self.check_env(verbose = False)

        print("Cleaning ...")
        self.clean(recreate_out = True) 

        print("Parse toc ...")
        toc = self.read_toc()

        print("Copy dependencies ...")
        self.copy_dependencies(toc)

        print("Generating document ...")
        self.generate_doc(self.generate_file_list(toc), pdf = pdf)
        
        cprint("Done ...", "green")

    def version(self):
        #uberdoc_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
        #uberdoc_dir = self.conf["doc_dir"]
        uberdoc_dir = os.path.abspath(self.conf["doc_dir"])
        env = [("GIT_WORK_TREE", uberdoc_dir), ("GIT_DIR", os.path.join(uberdoc_dir, ".git"))]
        
        returncode, version_str, error = self.cmd('git log -1 --format="%cd (%h)" --date=short', 
            cwd = uberdoc_dir,
            env = env) 

        if returncode > 0:
            cprint("Current dir is not a git repository.", "yellow")
            return datetime.datetime.now().strftime("%Y-%m-%d")
        else:
            version_str = version_str.rstrip()
            return version_str

    def git(self):
        """Turns the current dir into a git repo and adds default .gitignore"""
        print("Initializing git repo in current dir and adding files ...")
        uberdoc_dir = self.conf["doc_dir"]
        env = [("GIT_WORK_TREE", uberdoc_dir), ("GIT_DIR", os.path.join(uberdoc_dir, ".git"))]

        self.cmd('git init', echo = True, env = env)
        shutil.copyfile(resource_filename(__name__, "default_gitignore"), os.path.join(uberdoc_dir, ".gitignore"))
        self.cmd('git add .gitignore', echo = True, env = env)
        self.cmd('git add in', echo = True, env = env)
        self.cmd('git add uberdoc.cfg', echo = True, env = env)
        self.cmd('git commit -m "setup uberdoc document"', echo = True, env = env)

    def show(self):
        file_html = os.path.join(self.out_dir, self.conf["doc_filename"] + ".html")
        file_pdf = os.path.join(self.out_dir, self.conf["doc_filename"] + ".pdf")
        # on windows this should be
        #os.startfile(file_html)
        self.cmd("open " + file_html)
        if os.path.isfile(file_pdf):
            self.cmd("open " + file_pdf)

    def init_doc(self):
        """Generates an example in_dir dir structure, for new doc projects."""
        in_dir =  self.in_dir

        print("Copying default config file ...")
        shutil.copyfile(resource_filename(__name__, "uberdoc.cfg"), self.prefix_path("uberdoc.cfg"))

        print("Creating dir structure and sample chapters ...")
        
        os.mkdir(in_dir)
        os.makedirs(os.path.join(in_dir, "chapter1", "img"))
        os.makedirs(os.path.join(in_dir, "chapter2", "img"))   
        with open(os.path.join(in_dir, "toc.txt"), "w") as toc:
            toc.writelines(["chapter1\n", "chapter2\n"])
        with open(os.path.join(in_dir, "chapter1", "chapter1.md"), "w") as chapter1:
            chapter1.write("# Chapter 1 \n")
            chapter1.write("A sample chapter. \n")
        with open(os.path.join(in_dir, "chapter2", "chapter2.md"), "w") as chapter2:
            chapter2.write("# Chapter 2 \n")
            chapter2.write("A second sample chapter. \n")
    

    def check_env(self, verbose = True):
        def exit_if(condition, msg):
            if condition:
                print(colored(msg, "red"))
                sys.exit(1)

        if verbose:
            #print("Uberdoc version: " + __version__)
            cprint("Config settings: ", "yellow")
            if not self.isfile("uberdoc.cfg"):
                print("No project specific config file. Using defaults.")
            self.conf.show()    
            print("Document version: " + self.version())

        exit_if(
            not distutils.spawn.find_executable(self.conf["pandoc_cmd"]),
            "Error: Couldn't find pandoc in current path.")

        exit_if(
            not distutils.spawn.find_executable("git"),
            "Error: Couldn't find git in current path.") 

        exit_if(
            not os.path.isdir(self.in_dir),
            "Error: Couldn't find input folder. Was expecting folder: " + self.in_dir)

        toc_file_path = self.prefix_path(self.conf["in_dir"], self.conf["toc_filename"])
        exit_if(
            not os.path.isfile(toc_file_path),
            "Error: Couldn't find toc file. Was expecting: " + toc_file_path)

        if verbose: cprint("Environment setup ok.", "green")

    def prefix_path(self, *parts):
        return os.path.join(self.conf["doc_dir"], *parts)

    def isdir(self, adir):
        return os.path.isdir(self.prefix_path(adir))    

    def isfile(self, afile):
        return os.path.isfile(self.prefix_path(afile))    



def main():
    conf = Config("uberdoc.cfg")
    uberdoc = Uberdoc(conf);

    parser = argparse.ArgumentParser(
        description = "Wraps pandoc to create a writing environment for large documents.",
        epilog = "Now start writing and stop messing with your tools!")

    parser.add_argument("--version", action = "version", version = "Version " + __version__) 

    subparsers = parser.add_subparsers(help = "sub-command help")

    parser_clean = subparsers.add_parser("clean", help = "removes build artifacts")
    parser_clean.set_defaults(func = uberdoc.clean)

    parser_create = subparsers.add_parser(
        "init", 
        help = "inits the directory structure for a new document")
    parser_create.set_defaults(func = uberdoc.init_doc)

    parser_check = subparsers.add_parser(
        "check",
        help = "checks if your document environment is setup correctly")
    parser_check.set_defaults(func = uberdoc.check_env)

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
    parser_build.set_defaults(func = uberdoc.build)

    parser_git = subparsers.add_parser(
        "git", 
        help = "turns document dir into git repo")
    parser_git.set_defaults(func = uberdoc.git)

    parser_show = subparsers.add_parser(
        "show",
        help = "shows current document in browser")
    parser_show.set_defaults(func = uberdoc.show)

    args = parser.parse_args()
    if args.func == uberdoc.build:
        uberdoc.build(pdf = args.pdf) 
    else:
        args.func() 


if __name__ == "__main__":
    main()


    
