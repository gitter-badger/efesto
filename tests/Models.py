# -*- coding: utf-8 -*-
"""
    The models test case.

    Tests the efesto.Models package.
"""
import sys
sys.path.insert(0, "")
import pytest


from efesto.Models import Fields


@pytest.mark.parametrize('column', ['name', 'type', 'foreign', 'unique', 'description', 'label'])
def test_fields_model(column):
    """
    Tests the Fields model.
    """
    assert column in Fields.__dict__
