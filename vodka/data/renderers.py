"""
vodka data renderers, takes a dict and returns munge formatted
string 
"""

import munge
import munge.codec.all
import inspect

# DATA RENDERERS


class DataRenderer(object):

    def __init__(self, type="json"):
        self.type = type

    def render(self, data):
        cls = munge.get_codec(self.type)
        codec = cls()
        return codec.dumps(data)


class RPC(DataRenderer):
    
    """
    RPC renderer, renders an rpc response containing meta and data objects

    Should be used as a decorator. The decorated function will be called
    with the data container as first argument and the meta container referenced
    in the "meta" keyword argument.
    """

    def __init__(self, type="json", data_type=list, errors=False):
        super(RPC, self).__init__(type=type)
        self.errors = errors
        self.data_type = data_type

    def __call__(self, fn):
        def wrapped(*args, **kwargs):
            resp = {"meta": {}, "data": self.data_type()}
            try:
                i_args = inspect.getargspec(fn)
                if i_args.args and i_args.args[0] == "self":
                    fn(args[0], resp["data"], meta=resp[
                       "meta"], *args, **kwargs)
                else:
                    fn(resp["data"], meta=resp["meta"], *args, **kwargs)
            except Exception,  inst:
                if self.errors:
                    resp["meta"]["error"] = str(inst)
                else:
                    raise
            return self.render(resp)
        wrapped.__name__ = fn.__name__
        return wrapped
