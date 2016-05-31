#!/usr/bin/env python
from setuptools import setup, find_packages


setup(
    name = 'efesto',
    description='Efesto is a RESTful API generator based on the Falcon framework. ',
    url='https://github.com/vesuvium/efesto',
    author = 'Jacopo Cascioli',
    author_email='jacopocascioli@gmail.com',
    license='GPL3',
    version = '0.3.1',
    packages = find_packages(),
    tests_require = ['pytest', 'pytest-falcon'],
    setup_requires = ['pytest-runner'],
    install_requires = [
        'falcon==0.3.0',
        'psycopg2>=2.6.1',
        'peewee>=2.8.0',
        'itsdangerous>=0.24',
        'colorama>=0.3.3'
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Topic :: Internet :: WWW/HTTP',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    ]
)
