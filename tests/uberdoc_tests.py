from __future__ import print_function
from nose.tools import *
from uberdoc.udoc import Uberdoc, Config
import os
from os import path
import shutil


class TestUberdoc:
    BUILD_DIR = "testbuild"
    TEST_CONF_FILE = "tests/uberdoc_tests.cfg"

    def setup(self):
        self.conf = Config(self.TEST_CONF_FILE)
        self.conf['doc_dir'] = path.abspath("testbuild")
        self.u = Uberdoc(self.conf)
        self.clean()
        #self.out_dir = path.join(self.BUILD_DIR, self.conf["out_dir"])

        self.out_dir = self.u.prefix_path(self.conf["out_dir"])
        self.in_dir = self.u.prefix_path(self.conf["in_dir"])
        self.style_dir = self.u.prefix_path(self.conf["style_dir"])
        self.template_dir = self.u.prefix_path("templates")


    @with_setup(setup)
    def test_env(self):
        self.u.init_doc()
        self.u.check_env()

    @with_setup(setup)
    def test_init_doc(self):
        self.u.init_doc()
        in_dir = path.join(self.BUILD_DIR, self.conf["in_dir"])
        assert_true(path.isdir(in_dir))
        assert_true(path.isdir(path.join(in_dir, "chapter1")))
        assert_true(path.isdir(path.join(in_dir, "chapter2")))
        assert_true(path.isfile(path.join(self.BUILD_DIR, "uberdoc.cfg")))

    @with_setup(setup)
    def test_clean(self):
        os.mkdir(self.out_dir)
        assert_true(path.isdir(self.out_dir))
        self.u.clean(recreate_out = False)
        assert_false(path.isdir(self.out_dir))
        self.u.clean(recreate_out = True)
        assert_true(path.isdir(self.out_dir))

    @with_setup(setup)
    def test_read_toc(self):
        self.u.init_doc()
        lines = self.u.read_toc()
        assert_true(len(lines) == 3)
        assert_equals(lines[0], "chapter1")
        assert_equals(lines[1], "chapter2")

    @with_setup(setup)
    def test_version_with_git(self):
        self.u.init_doc()
        self.u.git()
        assert_true(path.isfile(path.join(self.BUILD_DIR, ".gitignore")))
        version = self.u.version()
        abs_doc_dir = path.abspath(self.conf["doc_dir"])
        env = [("GIT_WORK_TREE", abs_doc_dir), ("GIT_DIR", path.join(abs_doc_dir, ".git"))]
        returncode, version_str, error = self.u.cmd('git log -1 --format="%h" --date=short',
            cwd = abs_doc_dir,
            env = env)
        version_str = version_str.rstrip()
        assert_true(version.endswith("(" + version_str + ")"))

    @with_setup(setup)
    def test_build_html(self):
        self.u.init_doc()
        self.u.build()
        out_file = path.join(self.BUILD_DIR, self.conf["out_dir"], self.conf["doc_filename"])
        assert_true(path.isfile(out_file + ".html"))

    @with_setup(setup)
    def test_build_pdf(self):
        self.u.init_doc()
        self.u.build(pdf = True)
        out_file = path.join(self.BUILD_DIR, self.conf["out_dir"], self.conf["doc_filename"])
        assert_true(path.isfile(out_file + ".pdf"))

    @with_setup(setup)
    def test_conf(self):
        conf = Config(self.TEST_CONF_FILE)
        assert_equals(conf["in_dir"], "in")

    @with_setup(setup)
    def test_customize(self):
        self.u.init_doc()
        self.u.customize_templates()
        assert_true(path.isdir(self.style_dir))
        assert_true(path.isdir(self.template_dir))
        assert_true(path.isfile(path.join(self.template_dir, "default.tex")))
        self.u.customize_templates()

    @with_setup(setup)
    def test_copy_dependencies(self):
        self.u.init_doc()
        self.u.customize_templates()
        self.u.clean()
        self.u.copy_dependencies(toc_lines = self.u.read_toc())
        print(path.join(self.out_dir, "style"))
        assert_true(path.isdir(path.join(self.out_dir, "style")))

    @with_setup(setup)
    def test_outline(self):
        self.u.init_doc()
        toc = ["c1", "c2"]
        self.u.outline(toc = toc)
        assert_true(path.isdir(path.join(self.in_dir, "c1")))
        assert_true(path.isfile(path.join(self.in_dir, "c1",  "c1.md")))
        assert_true(path.isdir(path.join(self.in_dir, "c2")))
        assert_true(path.isfile(path.join(self.in_dir, "c2",  "c2.md")))
        assert_true(path.isdir(path.join(self.in_dir, "chapter1")))
        assert_true(path.isdir(path.join(self.in_dir, "chapter2")))

    def clean(self):
        if path.isdir(self.BUILD_DIR):
            shutil.rmtree(self.BUILD_DIR)
        os.mkdir(self.BUILD_DIR)