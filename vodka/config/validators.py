"""
All functions here can be passed as expected_type in config.Attribute instances

They should return a tuple of (bool, desc) where bool holds whether or not
the validation passed, and desc holds a description as to why not.

Desc can be None when passing
"""

import os


def path(value):
    return (os.path.exists(value), "path does not exist: %s" % value)
