"""
vodka data handlers, allows to modify data retrieved by
vodka data plugins
"""

import vodka.config
import vodka.component
import vodka.storage
import vodka.data.data_types
import vodka.util

handlers = {}


class register(vodka.util.register):
    class Meta(object):
        objects = handlers
        name = "data handler"


def get(handle):
    if handle not in handlers:
        raise KeyError("Data handler with handle %s does not exist" % handle)
    return handlers.get(handle)


def instantiate(cfg, data_id):
    cls = get(cfg.get("type"))
    return cls(cfg, data_id)


def instantiate_for_data_type(name, data_id=None):
    data_type = vodka.data.data_types.get(name)
    if not data_id:
        data_id = data_type
    r = []
    for h in data_type.handlers:
        r.append(instantiate(h, data_id))
    return r


class Handler(vodka.component.Component):

    """
    Base data handler class. A data handler can be attached to a data type
    to manipulate data of that type as it enters vodka.

    Attribues:
        config (dict or MungeConfg): configuration collection
        data_id (str): data id for this handler

    Classes:
        Configuration: Configuration Handler
    """

    class Configuration(vodka.config.ComponentHandler):
        pass

    def __init__(self, config, data_id):
        """
        Args:
            config (dict or MungeConfig): configuration collection
            data_id (str): data id for this handler, needs to be unique
        """
        self.config = config
        self.data_id = data_id
        self.init()

    def __call__(self, data, caller=None):
        pass

    def init(self):
        pass


@register("index")
class IndexHandler(Handler):
    
    """
    Will re-index data in a dictorary, indexed to the
    key specified in the config
    """

    class Configuration(Handler.Configuration):
        index = vodka.config.Attribute(
            str,
            help_text="the field to use for indexing"
        )

    def __call__(self, data, caller=None):
        data["data"] = dict([(d[self.get_config("index")], d)
                             for d in data["data"]])
        return data


@register("store")
class StorageHandler(Handler):
    
    """
    Will store the data in the vodka storage.
    Data will be stored using data type and data id as keys
    """

    class Configuration(Handler.Configuration):
        container = vodka.config.Attribute(
            str,
            help_text="specify how to store data",
            choices=["list", "dict"],
            default="list"
        )

        limit = vodka.config.Attribute(
            int,
            default=500,
            help_text="Limit the maximum amount of items to keep; only applies to list storage"
        )

        def validate_limit(self, value):
            if value < 1:
                return False, "Needs to be greater than 1"
            return True, ""

    def __call__(self, data, caller=None):

        if type(self.storage) == list:

            self.storage.append(data)
            l = len(self.storage)
            while l > self.get_config("limit"):
                self.storage.pop(0)
                l -= 1

        elif type(self.storage) == dict:

            self.storage.update(**data["data"])

        return data

    def init(self):
        if self.get_config("container") == "list":
            self.storage = vodka.storage.get_or_create(self.data_id, [])
        elif self.get_config("container") == "dict":
            self.storage = vodka.storage.get_or_create(self.data_id, {})
        else:
            raise ValueError("Unknown storage container type: %s" %
                             self.get_config("container"))
