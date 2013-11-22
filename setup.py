import sys
import os

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup
    from distutils.util import convert_path

    def _find_packages(where='.', exclude=()):
        """Return a list all Python packages found within directory 'where'

        'where' should be supplied as a "cross-platform" (i.e. URL-style) path; it
        will be converted to the appropriate local path syntax.  'exclude' is a
        sequence of package names to exclude; '*' can be used as a wildcard in the
        names, such that 'foo.*' will exclude all subpackages of 'foo' (but not
        'foo' itself).
        """
        out = []
        stack = [(convert_path(where), '')]
        while stack:
            where, prefix = stack.pop(0)
            for name in os.listdir(where):
                fn = os.path.join(where, name)
                if ('.' not in name and os.path.isdir(fn) and
                        os.path.isfile(os.path.join(fn, '__init__.py'))):
                    out.append(prefix+name)
                    stack.append((fn, prefix + name + '.'))
        for pat in list(exclude)+['ez_setup', 'distribute_setup']:
            from fnmatch import fnmatchcase
            out = [item for item in out if not fnmatchcase(item, pat)]
        return out

    find_packages = _find_packages

#with open('LICENSE') as fp:
#    license = fp.read()

setup(
    name = 'uberdoc',
    version = '1.2.2',
    packages = find_packages('.', exclude=('tests',)),
    description = 'Pandoc wrapper for large, multi-chapter documents.',
    author='Stephan Brosinski',
    author_email='sbrosinski@gmail.com',
    url = 'http://github.com/sbrosinski/uberdoc',
    download_url = 'http://github.com/sbrosinski/uberdoc',
    license = "license",
	keywords = ["pandoc", "markdown"],
    classifiers = [
        "Programming Language :: Python",
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Environment :: Other Environment",
        "Intended Audience :: Developers"
        ],
    #package_dir={'': 'uberdoc'},
    package_data={'': ['templates/*.*', 'style/*.*', 'sample/*.*', 'uberdoc.cfg', 'default_gitignore']},
    include_package_data = True,
    entry_points = {
    	'console_scripts': [
    		'udoc = uberdoc.udoc:main'
    	]
    },
    install_requires=['jinja2']
)
