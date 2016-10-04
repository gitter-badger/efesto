#!/usr/bin/env python
import io
from setuptools import find_packages, setup


readme = io.open('README.rst', 'r', encoding='utf-8').read()

setup(
    name='efesto',
    description='RESTful (micro)server that can build an API in minutes.',
    long_description=readme,
    url='https://github.com/getefesto/efesto',
    author='Jacopo Cascioli',
    author_email='jacopocascioli@gmail.com',
    license='GPL3',
    version='0.7',
    packages=find_packages(),
    tests_require=[
        'pytest',
        'pytest-falcon'
    ],
    setup_requires=['pytest-runner'],
    install_requires=[
        'falcon==1.0.0',
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
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    ],
    entry_points='''
        [console_scripts]
        efesto-quickstart=efesto.scripts.quickstart:quickstart
        efesto-blueprints=efesto.scripts.blueprints:blueprints
    '''
)
