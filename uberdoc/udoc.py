#!/usr/bin/env python

"""Wrapper script for pandoc. Useful for larger documents, since it breaks up
several e.g. markdown files into chapters and provides a build process to
generate html and pdf docs from them.
"""
from __future__ import print_function
import os
from os import path
import argparse
import sys
import subprocess
import shlex
import shutil
import distutils.spawn
import pkg_resources
import datetime
from pkg_resources import resource_filename
from jinja2 import Template, Environment, FileSystemLoader
from .config import Config

if sys.version_info[0] > 2:
    from .termcolor import colored, cprint
else:
    from termcolor import colored, cprint

__author__ = "Stephan Brosinski"
__version__ = "1.2.2"

# todo
# when reading vars from config file, reading from the user section should return only
# user sections vars, not default section vars
# - "View Source" Feature in HTML, see the Markup?
# - "Jump direkectly to markdown File from HTML" - Feature?

class Uberdoc:

    def __init__(self, conf):
        self.conf = conf
        self.out_dir = self.prefix_path(self.conf["out_dir"])
        self.in_dir = self.prefix_path(self.conf["in_dir"])
        self.style_dir = self.prefix_path(self.conf["style_dir"])
        self.template_dir = self.prefix_path("templates")

    def cmd(self, cmdStr, verbose=False, cwd='.', echo=False, env=[]):
        """Executes cmdStr as shell command in the working directory provided
        by cwd
        """

        if echo:
            print(cmdStr)

        for key, value in env:
            os.environ[key] = value

        cmd_env = os.environ

        if verbose:
            print('-------- executing cmd -------------')
            print('cmd: ' + cmdStr + '\n')
            print('cwd: ' + cwd + '\n')
            print('env: ' + str(cmd_env) + '\n')

        process = subprocess.Popen(shlex.split(cmdStr),
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   cwd=cwd,
                                   env=cmd_env)

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
            files.append(path.join(line, line + self.conf["input_ext"]))
        return files

    def preprocess(self, files):
        template_dir = os.path.join(self.out_dir, self.conf["in_dir"])
        env = Environment(loader=FileSystemLoader(template_dir))
        doc_version = self.version()
        user_conf_items = self.conf.user_items()

        for input_file in files:
            print("Preprocessing " + input_file)

            template_vars = {
                "udoc": {
                    "version": __version__,
                    "doc_version": doc_version,
                    "md_file": input_file
                },
                "conf": user_conf_items
            }

            template = env.get_template(input_file)
            content = template.render(template_vars)
            complete_input_file = os.path.join(self.out_dir, self.conf["in_dir"], input_file)

            with open(complete_input_file, 'w') as fout:
                content_enc = content.encode('utf-8')
                fout.write(content_enc)



    def generate_doc(self, files, pdf=False, verbose=False):
        """Calls pandoc to generate html, and optionally PDF docs"""
        file_list = " ".join(files)

        out_file = path.join(path.abspath(self.out_dir), self.conf["doc_filename"])

        html_template = path.abspath(
            path.join(self.conf["doc_dir"], "templates", "default.html"))
        if path.isfile(html_template):
            template = ' --template=' + html_template
        else:
            template = ' --template=' + \
                resource_filename(__name__, "templates/default.html")

        pandoc_wd = path.join(self.out_dir, self.conf["in_dir"])

        # always build html doc
        build_cmd = " ".join([
            self.conf["pandoc_cmd"],
            self.conf["pandoc_options_html"],
            ' -V VERSION:"{0}" '.format(self.version()),
            template,
            file_list,
            "-o",
            out_file + ".html"])
        self.cmd(build_cmd, cwd=pandoc_wd, verbose=verbose)

        # build pdf in addition, if required (takes a lot longer)
        if pdf:
            # check if doc dir has tex template, if not use default
            tex_template = path.abspath(
                path.join(self.conf["doc_dir"], "templates", "default.tex"))
            if path.isfile(tex_template):
                template = ' --template=' + tex_template
            else:
                template = ' --template=' + \
                    resource_filename(__name__, "templates/default.tex")

            build_cmd = " ".join([
                                 self.conf["pandoc_cmd"],
                                 self.conf["pandoc_options_pdf"],
                                 ' -V VERSION:"{0}" '.format(self.version()),
                                 template,
                                 file_list,
                                 "-o",
                                 out_file + ".pdf"])
            self.cmd(build_cmd, cwd=pandoc_wd, verbose=verbose)

    def clean(self, recreate_out=False):
        """Recreates out_dir"""
        print("removing " + self.out_dir)
        if path.isdir(self.out_dir):
            shutil.rmtree(self.out_dir)
            print("removed")
        if recreate_out:
            os.mkdir(self.out_dir)

    def copy_dependencies(self, toc_lines):
        """Copies the contents of style_dir (e.g. css files) to out_dir.
        Chapters with images will have their images copied there as
        well, while preserving the chapter dir structure
        """
        if path.isdir(self.style_dir):
            shutil.copytree(
                self.style_dir,
                path.join(self.out_dir, self.conf["style_dir"]))
        else:
            shutil.copytree(
                resource_filename(__name__, "style"),
                path.join(self.out_dir, self.conf["style_dir"]))

        for line in toc_lines:
            img_dir = self.conf["img_dir"]
            if path.isdir(path.join(self.in_dir, line, img_dir)):
                os.mkdir(path.join(self.out_dir, line))

                shutil.copytree(
                    path.join(self.in_dir, line, img_dir),
                    path.join(self.out_dir, line, img_dir))

        shutil.copytree(self.in_dir, os.path.join(self.out_dir, self.conf["in_dir"]))


    def customize_templates(self):
        if path.isdir(self.template_dir):
            shutil.rmtree(self.template_dir)

        print("Creating templates ...")
        shutil.copytree(
            resource_filename(__name__, "templates"),
            self.template_dir)

        if path.isdir(self.style_dir):
            shutil.rmtree(self.style_dir)

        print("Creating styles ...")
        shutil.copytree(
            resource_filename(__name__, "style"),
            self.style_dir)

    def read_toc(self):
        """Reads the toc file containing the chapter list."""
        toc_file = path.join(self.in_dir, self.conf["toc_filename"])
        try:
            with open(toc_file) as f:
                lines = f.read().splitlines()
            forced_lines = [line for line in lines if line.startswith("!")]
            if len(forced_lines) > 0:
                return [line[1:] for line in forced_lines]
            else:
                return [line for line in lines if not line.startswith("#")]
        except Exception:
            cprint("Can't read " + toc_file, "red")
            sys.exit(1)

    def outline(self, toc=None, delete=False):
        if toc is None:
            toc = self.read_toc()
        for toc_entry in toc:
            chapter_dir = path.join(self.in_dir, toc_entry)
            chapter_file = path.join(
                chapter_dir, toc_entry + self.conf["input_ext"])
            if not path.isdir(chapter_dir):
                os.mkdir(chapter_dir)
                cprint("Creating: " + toc_entry +
                       " -> " + chapter_file, "yellow")
                with open(chapter_file, "w") as chapter_md:
                    chapter_md.write("# " + toc_entry + "\n")
            else:
                cprint("Exists: " + toc_entry + " -> " + chapter_file, "green")
        self._check_chapter_dirs(toc, delete)

    def _check_chapter_dirs(self, toc, delete=False):
        all_chapter_dirs = [name for name in os.listdir(self.in_dir)
                            if os.path.isdir(os.path.join(self.in_dir, name))]
        for chapter_dir_name in all_chapter_dirs:
            if not chapter_dir_name in toc:
                chapter_dir = path.join(self.in_dir, chapter_dir_name)
                chapter_file = path.join(
                    chapter_dir, chapter_dir_name + self.conf["input_ext"])
                cprint(
                    "Missing: " + chapter_dir_name + " -> " + chapter_file, "red")
                if delete:
                    should_remove = raw_input(
                        "Remove " + chapter_dir_name + "? (y/N): ")
                    if should_remove == "y":
                        shutil.rmtree(chapter_dir)

    def build(self, pdf=False, verbose=False):
        """Calls all steps of the doc build process"""
        print("Check environment ...")
        self.check_env(verbose=verbose)

        print("Cleaning ...")
        self.clean(recreate_out=True)

        print("Parse toc ...")
        toc = self.read_toc()

        print("Copy dependencies ...")
        self.copy_dependencies(toc)

        print("Preprocessing input files ...")
        files = self.generate_file_list(toc)
        self.preprocess(files)

        print("Generating document ...")
        self.generate_doc(files, pdf=pdf, verbose=verbose)

        cprint("Done ...", "green")

    def version(self):
        uberdoc_dir = path.abspath(self.conf["doc_dir"])

        git_dir = self._find_closest_git_dir(uberdoc_dir)
        if git_dir is None:
            return datetime.datetime.now().strftime("%Y-%m-%d")

        env = [("GIT_WORK_TREE", uberdoc_dir), ("GIT_DIR", git_dir)]

        returncode, version_str, error = self.cmd(
            'git log -1 --format="%cd (%h)" --date=short',
            cwd=uberdoc_dir,
            env=env)

        if returncode > 0:
            cprint("Current dir is not a git repository.", "yellow")
            return datetime.datetime.now().strftime("%Y-%m-%d")
        else:
            version_str = version_str.rstrip()
            return version_str

    def _find_closest_git_dir(self, startdir):
        currentdir = path.abspath(startdir)
        while currentdir != "/":
            if path.isdir(path.join(currentdir, ".git")):
                return path.join(currentdir, ".git")
            currentdir = path.abspath(path.join(currentdir, os.pardir))
        return None

    def git(self):
        """Turns the current dir into a git repo and adds default .gitignore"""
        print("Initializing git repo in current dir and adding files ...")
        uberdoc_dir = self.conf["doc_dir"]
        env = [("GIT_WORK_TREE", uberdoc_dir),
               ("GIT_DIR", path.join(uberdoc_dir, ".git"))]

        self.cmd('git init', echo=True, env=env)
        shutil.copyfile(
            resource_filename(__name__, "default_gitignore"), path.join(uberdoc_dir, ".gitignore"))
        self.cmd('git add .gitignore', echo=True, env=env)
        self.cmd('git add in', echo=True, env=env)
        self.cmd('git add uberdoc.cfg', echo=True, env=env)
        self.cmd('git commit -m "setup uberdoc document"', echo=True, env=env)

    def show(self):
        file_html = path.join(
            self.out_dir, self.conf["doc_filename"] + ".html")
        file_pdf = path.join(self.out_dir, self.conf["doc_filename"] + ".pdf")
        # on windows this should be
        # os.startfile(file_html)
        self.cmd("open " + file_html)
        if path.isfile(file_pdf):
            self.cmd("open " + file_pdf)

    def init_doc(self):
        """Generates an example in_dir dir structure, for new doc projects."""
        in_dir = self.in_dir

        print("Copying default config file " + resource_filename(__name__, "uberdoc.cfg"))
        shutil.copyfile(
            resource_filename(__name__, "uberdoc.cfg"), self.prefix_path("uberdoc.cfg"))

        print("Creating dir structure and sample chapters ...")

        shutil.copytree(
            resource_filename(__name__, "sample"),
            in_dir)

    def check_env(self, verbose=True):
        def exit_if(condition, msg):
            if condition:
                print(colored(msg, "red"))
                sys.exit(1)

        if verbose:
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
            not path.isdir(self.in_dir),
            "Error: Couldn't find input folder. Was expecting folder: " + self.in_dir)

        toc_file_path = self.prefix_path(
            self.conf["in_dir"], self.conf["toc_filename"])
        exit_if(
            not path.isfile(toc_file_path),
            "Error: Couldn't find toc file. Was expecting: " + toc_file_path)

        if verbose:
            cprint("Environment setup ok.", "green")

    def prefix_path(self, *parts):
        return path.join(self.conf["doc_dir"], *parts)

    def isdir(self, adir):
        return path.isdir(self.prefix_path(adir))

    def isfile(self, afile):
        return path.isfile(self.prefix_path(afile))


def main():
    conf = Config("uberdoc.cfg", defaults={"doc_dir": "."})
    uberdoc = Uberdoc(conf)

    parser = argparse.ArgumentParser(
        description="Wraps pandoc to create a writing environment for large documents.",
        epilog="Now start writing and stop messing with your tools!")

    parser.add_argument(
        "--version", action="version", version="Version " + __version__)

    subparsers = parser.add_subparsers(help="sub-command help")

    parser_clean = subparsers.add_parser(
        "clean", help="removes build artifacts")
    parser_clean.set_defaults(func=uberdoc.clean)

    parser_create = subparsers.add_parser(
        "init",
        help="inits the directory structure for a new document")
    parser_create.set_defaults(func=uberdoc.init_doc)

    parser_check = subparsers.add_parser(
        "check",
        help="checks if your document environment is setup correctly")
    parser_check.set_defaults(func=uberdoc.check_env)

    parser_build = subparsers.add_parser(
        "build",
        help="generates the document")
    parser_build.add_argument(
        "-p",
        "--pdf",
        help="also creates a PDF version",
        action="store_true")
    parser_build.add_argument(
        "-v",
        "--verbose",
        help="gives more details on what is happening during conversion",
        action="store_true")
    parser_build.set_defaults(func=uberdoc.build)

    parser_git = subparsers.add_parser(
        "git",
        help="turns document dir into git repo")
    parser_git.set_defaults(func=uberdoc.git)

    parser_show = subparsers.add_parser(
        "show",
        help="shows current document in browser")
    parser_show.set_defaults(func=uberdoc.show)

    parser_customize = subparsers.add_parser(
        "customize",
        help="duplicates default templates and styles for customizing")
    parser_customize.set_defaults(func=uberdoc.customize_templates)

    parser_outline = subparsers.add_parser(
        "outline",
        help="creates markdown files and directories from toc")
    parser_outline.add_argument(
        "-d",
        "--delete",
        help="delete chapter dirs not in toc",
        action="store_true")
    parser_outline.set_defaults(func=uberdoc.outline)

    args = parser.parse_args()
    if args.func == uberdoc.build:
        uberdoc.build(pdf=args.pdf, verbose=args.verbose)
    elif args.func == uberdoc.outline:
        uberdoc.outline(delete=args.delete)
    else:
        args.func()


if __name__ == "__main__":
    main()
