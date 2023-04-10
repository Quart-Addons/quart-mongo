"""
Odmantic models for testing.
"""
from odmantic import Field, Model

class Things(Model):
    """
    Things collection model using ODMantic.
    """
    id: str = Field(primary_field=True)
    val: str

class ThingsOne(Model):
    """
    Things collection model using ODMantic.
    """
    id: str = Field(primary_field=True)
    val: str
    val_1: str

class ThingsTwo(Model):
    """
    Things collection model using ODMantic.
    """
    id: str = Field(primary_field=True)
    val: str
    val_1: str
    val_2: str

class InvalidModel(object):
    """
    Invalid model object.
    """
