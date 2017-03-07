# -*- coding: utf-8 -*-
"""
"""
from efesto.models import Types
from peewee import BaseModel

def test_model_creation():
    model_type = Types()
    model = model_type.create_model()
    assert isinstance(model, BaseModel)
