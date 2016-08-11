import vodka.config
import vodka.component

data_types = {}


def instantiate_from_config(cfg):
    """Instantiate data types from config"""
    for h in cfg:
        if h.get("type") in data_types:
            raise KeyError("Data type '%s' already exists" % h)
        data_types[h.get("type")] = DataType(h)


def get(name):
    """
    Get data type class by data type name

    Args:
        name (str): data type name

    Returns:
        the data type class with the matching name

    Raises:
        KeyError: Unknown data type
    """
    if name not in data_types:
        raise KeyError("Unknown data type '%s'" % name)
    return data_types.get(name)


class DataType(vodka.component.Component):

    """
    Base class for all data types
    
    Classes:
        Configuration: configuration handler
    """

    class Configuration(vodka.config.ComponentHandler):
        handlers = vodka.config.Attribute(
            list,
            default=[],
            help_text="data handlers to apply to this data"
        )

    @property
    def handlers(self):
        """ handlers specified for this data type via config"""
        return self.get_config("handlers")

    def __init__(self, config):
        self.config = config
