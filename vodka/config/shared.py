"""
Allows sharing of configuration keys between different vodka apps
"""
from vodka.config import Handler, Attribute as BaseAttribute
import vodka.util

shared = {}

MODE_MERGE = 1
MODE_APPEND = 2

MODES = {
    "merge" : MODE_MERGE,
    "append" : MODE_APPEND
}

ROUTERS = {}

class register(vodka.util.register):
    class Meta(object):
        name = "shared config router"
        objects = ROUTERS


class Attribute(BaseAttribute):
    """
    Extended config attribute that takes a "share" argument in
    that allows it to be shared between differen applications
    """

    def __init__(self, expected_type, **kwargs):
        """
        Kwargs:
            share(str): if set will initialize the apropriate sharing router
                format: "{sharing_id}:{sharing_mode}"
                example: "test:merge"
        """

        super(Attribute, self).__init__(expected_type, **kwargs)
        share = kwargs.get("share","")
        self.share = None
        if share:
            sharing_id, sharing_mode = tuple(share.split(":"))
            self.share = ROUTERS[expected_type](sharing_id, mode=sharing_mode)

    def finalize(self, cfg, key_name, value, **kwargs):
        if self.share:
            cfg[key_name] = self.share.share(key_name, value)


class Container(Attribute):

    def finalize(self, cfg, key_name, value, **kwargs):
        return

    def preload(self, cfg, key_name, **kwargs):
        if self.share:
            if cfg.get(key_name) is not None:
                for _k, _v in cfg.get(key_name,{}).items():
                    self.share.share(_k, _v)
            if self.default is not None:
                for _k, _v in self.default.items():
                    self.share.share(_k, _v)
                cfg[key_name] = self.share.container



class Router(object):
    """
    Config sharing router, will redirect shared config attributes
    to a common container
    """
    def __init__(self, _id, mode=MODE_MERGE):
        if not _id:
            raise ValueError("Name must be specified for config sharing router")
        self.id = _id
        self.mode = MODES.get(mode)
        if not self.mode:
            raise ValueError("Invalid mode specified for config sharing router: %s" % mode)

    def __repr__(self):
        return "%s <%s>" % (self.__class__.__name__, self.id)

    @property
    def container(self):
        return shared.get(self.id,{})

    @property
    def container_type(self):
        return None

    @property
    def empty(self):
        if self.container_type:
            ct = self.container_type
            return ct()
        return None

    def share(self, name, value):
        if not self.id in shared:
            shared[self.id] = {}
        if not name in shared[self.id]:
            shared[self.id][name] = self.empty

        if type(value) != self.container_type:
            raise ValueError("Router '%s' only accepts value of type '%s'"%(self.id, self.container_type))

        return shared[self.id][name]

@register(list)
class ListRouter(Router):

    """
    Config sharing router for list configs
    """

    @property
    def container_type(self):
        return list

    def share(self, name, value):
        container = super(ListRouter,self).share(name,value)

        if self.mode == MODE_MERGE:
            for v in value:
                if v not in container:
                    container.append(v)
        elif self.mode == MODE_APPEND:
            for v in value:
                container.append(v)

        return container

@register(dict)
class DictRouter(Router):

    """
    Config sharing router for dict configs
    """

    @property
    def container_type(self):
        return dict

    def get(self, key, default=None):
        return self.container.get(key, default)

    def share(self, name, value):
        container = super(DictRouter,self).share(name,value)

        if self.mode == MODE_MERGE:
            container.update(**value)
        elif self.mode == MODE_APPEND:
            raise ValueError("DictRouter cannot have mode: 'append'")

        return container

class RoutersHandler(Handler):
    """
    Extend this handler in order to do nested config sharing with the same
    sharing ruleset
    """
    mode = "merge"
    sharing_id = None
    router_cls = DictRouter

    @classmethod
    def finalize(cls, cfg, key_name, value, **kwargs):
        router_cls = cls.router_cls
        share = router_cls(cls.sharing_id, mode=cls.mode)
        attr_name = kwargs.get("attr_name")
        parent_cfg = kwargs.get("parent_cfg")
        share.share(key_name, value)
        parent_cfg[attr_name] = shared[cls.sharing_id]

def Routers(typ, share, handler=RoutersHandler):
    """
    Pass the result of this function to the handler argument
    in your attribute declaration
    """
    _sharing_id, _mode = tuple(share.split(":"))
    _router_cls = ROUTERS.get(typ)
    class _Handler(handler):
        mode=_mode
        sharing_id=_sharing_id
        router_cls=_router_cls
    return _Handler
