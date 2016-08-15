#!/usr/bin/env python
from setuptools import find_packages, setup


setup(
    name='efesto',
    description='Efesto is a RESTful API generator based on the Falcon.',
    url='https://github.com/vesuvium/efesto',
    author='Jacopo Cascioli',
    author_email='jacopocascioli@gmail.com',
    license='GPL3',
    version='0.5.0',
    packages=find_packages(),
    tests_require=[
        'pytest',
        'pytest-falcon==0.3.3'
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
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    ],
    entry_points='''
        [console_scripts]
        efesto-quickstart=efesto.scripts.quickstart:quickstart
        efesto-blueprints=efesto.scripts.blueprints:blueprints
    '''
)
