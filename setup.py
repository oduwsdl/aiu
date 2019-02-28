import os
import codecs
import re

from setuptools import setup
from setuptools.command.install import install as _install
from os import path

# Python packaging info: http://python-packaging.readthedocs.io/en/latest/index.html
# More Python packaging info: http://python-packaging-user-guide.readthedocs.io/tutorials/distributing-packages/
# Python version info: https://www.python.org/dev/peps/pep-0440/

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

here = os.path.abspath(os.path.dirname(__file__))

# taken from https://packaging.python.org/guides/single-sourcing-package-version/
def read(*parts):
    with codecs.open(os.path.join(here, *parts), 'r') as fp:
        return fp.read()

def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

setup(
    name='aiu',
    # cmdclass={'install': Install},
    version=find_version("aiu", "version.py"),
    description='Tools for for interacting with Archive-It.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/oduwsdl/archiveit_utilities',
    author='Shawn M. Jones',
    author_email='jones.shawn.m@gmail.com',
    license='MIT',
    packages=['aiu'],
    scripts=['bin/seeds2warc', 'bin/tm2warc', 'bin/fetch_ait_metadata', 'bin/generate_seed_statistics'],
    install_requires=[
        'requests_futures',
        'warcio',
        'requests',
        'bs4',
        'html5lib',
        'requests_cache'
    ],
    # setup_requires=['nltk'],
    test_suite="tests",
    zip_safe=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='webarchives memento'
    )
