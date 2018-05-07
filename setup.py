from setuptools import setup
from setuptools.command.install import install as _install
from os import path

# Python packaging info: http://python-packaging.readthedocs.io/en/latest/index.html
# More Python packaging info: http://python-packaging-user-guide.readthedocs.io/tutorials/distributing-packages/
# Python version info: https://www.python.org/dev/peps/pep-0440/

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='aiu',
    # cmdclass={'install': Install},
    version='0.1a0',
    description='Tools for for interacting with Archive-It.',
    long_description=long_description,
    url='https://github.com/shawnmjones/archiveit_utilities',
    author='Shawn M. Jones',
    author_email='jones.shawn.m@gmail.com',
    license='MIT',
    packages=['aiu'],
    scripts=['bin/seeds2warc'],
    install_requires=[
        'requests_futures',
        'warcio',
        'requests',
        'bs4'
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