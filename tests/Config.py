# -*- coding: utf-8 -*-
"""
    The Config test case.

    Tests the Config module.
"""
import sys
sys.path.insert(0, "")
import pytest


from efesto.Config import Config


@pytest.fixture
def config():
    return Config()


def test_find_path_exception(config):
    """
    Tests the find_path method behaviour when called with a non-existing path.
    """
    with pytest.raises(ValueError) as e_info:
        config.find_path('somerandomname')
