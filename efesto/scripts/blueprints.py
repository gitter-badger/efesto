# -*- coding: utf-8 -*-
"""
    Efesto blueprints script.

    This script will load / dump blueprints.
"""
import argparse
import os

from efesto.Blueprints import dump_blueprint, load_blueprint


def blueprints():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dump', dest='dump')
    parser.add_argument('--load', dest='load')
    args = parser.parse_args()
    if args.load:
        path = os.path.join(os.getcwd(), args.load)
        if os.path.isfile(path):
            load_blueprint(path)
            print("Blueprint loaded successfully!")
        else:
            print("The provided path is not a file.")

    if args.dump:
        path = os.path.join(os.getcwd(), args.dump)
        dump_blueprint(path)
        print("Blueprint dumped successfully!")
