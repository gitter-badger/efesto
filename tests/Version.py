# -*- coding: utf-8 -*
"""
    The Version test case.
"""
import sys
sys.path.insert(0, "")

import efesto


def test_version():
    assert type(efesto.__version__) == str
