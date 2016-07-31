storage = {}

def get(name, default=None):
    return storage.get(name, default)

def get_or_create(name,  value):

    """
    returns the storage space defined by name

    if space does not exist yet it will first be created with the
    specified value
    """
    
    if name not in storage:
        storage[name] = value
    return storage[name]
