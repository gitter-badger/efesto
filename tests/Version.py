# -*- coding: utf-8 -*
"""
    The Version test case.
"""
import sys
import efesto


sys.path.insert(0, '')


def test_version():
    assert type(efesto.__version__) == str
