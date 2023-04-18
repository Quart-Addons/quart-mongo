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

class InvalidModel(object):
    """
    Invalid model object.
    """
