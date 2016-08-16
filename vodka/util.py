def dict_get_path(data, path, default=None):
    """
    Returns the value inside nested structure of data located
    at period delimited path
    
    When traversing a list, as long as that list is containing objects of 
    type dict, items in that list will have their "name" and "type" values 
    tested against the current key in the path.

    Args:
        data (dict or list): data to traverse
        path (str): '.' delimited string
    
    Kwargs:
        default: value to return if path does not exist
    """

    keys = path.split(".") 
    for k in keys:
        if type(data) == list:
            found = False
            for item in data:
                name = item.get("name", item.get("type"))
                if name == k:
                    found = True
                    data = item
                    break
            if not found:
                return default
        elif type(data) == dict:
            if k in data:
                data = data[k]
            else:
                return default
        else:
            return default
    return data 


class register(object):

    """
    allows you index a class in a register
   
    can be used as a decorator
    """

    class Meta(object):
        name = "object"
        objects = {}
    
    def __init__(self, handle):
        
        """
        Args:
            handle (str): unique class handle 

        Raises:
            KeyError: class with handle already exists"
        """
 
        if handle in self.Meta.objects:
            raise KeyError("%s with handle '%s' already registered" % (self.Meta.name, handle))
        self.handle = handle


    def __call__(self, cls):
        cls.handle = self.handle
        self.Meta.objects[cls.handle] = cls
        return cls
