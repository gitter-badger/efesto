# -*- coding: utf-8 -*-
"""
    The models test case.

    Tests the efesto.Models package.
"""
import sys
sys.path.insert(0, "")
import pytest


from efesto.Models import Fields, Users


@pytest.mark.parametrize('column',
    ['id', 'name', 'email', 'password', 'rank', 'last_login']
)
def test_users_model(column):
    """
    Tests the Users model.
    """
    assert column in Users.__dict__


@pytest.mark.parametrize('column', ['id', 'name', 'type', 'foreign', 'unique', 'description', 'label'])
def test_fields_model(column):
    """
    Tests the Fields model.
    """
    assert column in Fields.__dict__
