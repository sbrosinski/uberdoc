#from distutils.core import setup
from setuptools import setup

setup(
    name = 'uberdoc',
    py_modules = ['uberdoc'],
    version = '1.0.0',
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
    entry_points = {
    	'console_scripts': [
    		'uberdoc = uberdoc:main'
    	]
    }
)