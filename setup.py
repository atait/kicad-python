#!/usr/bin/env python
import setuptools

try:
    reqs = open('requirements.txt', 'r').read().splitlines()
except IOError:
    reqs = []

def readme():
    with open('README.md', 'r') as fx:
      return fx.read()

setuptools.setup(
        name='kigadgets',
        version='0.4.1',
        description='Cross-version python wrapper for KiCAD pcbnew',
        long_description=readme(),
        long_description_content_type='text/markdown',
        author='Piers Titus van der Torren, Miguel Angel Ajo, Hasan Yavuz Ozderya, Alex Tait',
        author_email='atait@ieee.org',
        license='GPL v2',
        url='https://github.com/atait/kicad-python/',
        packages=setuptools.find_packages(exclude=['tests']),
        install_requires=reqs,
        entry_points={'console_scripts': 'link_kicad_python_to_pcbnew=kicad.environment:cl_main'},
    )
