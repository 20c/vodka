"""
All functions here can be passed as expected_type in config.Attribute instances

They should return a tuple of (bool, desc) where bool holds whether or not
the validation passed, and desc holds a description as to why not.

Desc can be None when passing
"""

import os


def path(value):
    """ Validates that the value is an existing path """
    if not value:
        return (True, "")
    return (os.path.exists(value), "path does not exist: %s" % value)

def host(value):
    """ Validates that the value is a valid network location """
    if not value:
        return (True, "")
    try:
        host,port = value.split(":")
    except ValueError as _:
        return (False, "value needs to be <host>:<port>")

    try:
        int(port)
    except ValueError as _:
        return (False, "port component of the host address needs to be a number")

    return (True, "")

