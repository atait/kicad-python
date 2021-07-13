#!/usr/bin/env python
import setuptools

try:
    reqs = open('requirements.txt', 'r').read().splitlines()
except IOError:
    reqs = []

setuptools.setup(
        name='kicad',
        version='0.2',
        description='KiCad python API',
        author='Piers Titus van der Torren, KiCad Developers, Hasan Yavuz Ozderya, Alex Tait',
        author_email='kicad-developers@lists.launchpad.net',
        url='https://github.com/kicad/kicad-python/',
        packages=setuptools.find_packages(exclude=['ez_setup']),
        zip_safe=False,
        install_requires=reqs,
        entry_points={'console_scripts': 'link_kicad_python_to_pcbnew=kicad.environment:cl_main'},
        test_suite='kicad.test.unit')
