import pluginmgr 
import imp
import sys

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


class SearchPathImporter(pluginmgr.SearchPathImporter):

    """
    FIXME: this s a temporary solution until the
    two functions are fixed in pluginmgr.SearchPathImporter
    """
    
    # import hooks
    def find_module(self, fullname, path=None):
        if self.create_loader:
            if fullname == self.package:
                try:
                    self.load_module(fullname)
                except ImportError:
                    return self
            if fullname == self.namespace:
                return self

        m = self.re_ns.match(fullname)

        if not m:
            return

        name = m.group(1)
        if self.find_file(name):
            return self
 

    def load_module(self, name): 
        # build package for loader if it doesn't exist
        # don't need to check for create_loader here, checks in find_module
        if name == self.package or name == self.namespace:
            # make a new loader module
            mod = imp.new_module(name)

            # Set a few properties required by PEP 302
            mod.__file__ = self.namespace
            mod.__name__ = name
            mod.__path__ = self.searchpath
            mod.__loader__ = self
            mod.__package__ = '.'.join(name.split('.')[:-1])
            sys.modules[name] = mod
            return mod

        m = self.re_ns.match(name)

        if not m:
            raise ImportError(name)

        modulename = m.group(1)
        filename = self.find_file(modulename)
        mod = imp.load_source(name, filename)
        sys.modules[name] = mod
        return mod


