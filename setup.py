#from distutils.core import setup
from setuptools import setup, find_packages

setup(
    name = 'uberdoc',
    version = '1.0.0',
    packages = find_packages('src'),
    description = 'Pandoc wrapper for large, multi-chapter documents.',
    author='Stephan Brosinski',
    author_email='sbrosinski@gmail.com',
    url = 'http://github.com/sbrosinski/uberdoc',
	keywords = ["pandoc", "markdown"],
    classifiers = [
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Environment :: Other Environment",
        "Intended Audience :: Developers"
        ],
    package_dir={'':'src'},
    package_data={'uberdoc': ['templates/*.*', 'style/*.*', 'uberdoc.cfg']},
    include_package_data = True,
    entry_points = {
    	'console_scripts': [
    		'uberdoc = uberdoc.uberdoc:main'
    	]
    }
)