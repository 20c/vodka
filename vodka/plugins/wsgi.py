import os 
from vodka import get_instance
import vodka.plugins
import vodka.config
import vodka.config.validators


def application():
    return WSGIPlugin.wsgi_application

class SSLConfiguration(vodka.config.Handler):
    
    """
    Allows you to configure the ssl context of a wsgi
    plugin
    """
    
    enabled = vodka.config.Attribute(
        bool,
        default=False,
        help_text="enable ssl encryption"
    )

    key = vodka.config.Attribute(
        vodka.config.validators.path,
        default="",
        help_text="location of your ssl private key file"
    )

    cert = vodka.config.Attribute(
        vodka.config.validators.path,
        default="",
        help_text="location of your ssl certificate file"
    )


class WSGIPlugin(vodka.plugins.PluginBase):

    wsgi_application = None

    class Configuration(vodka.plugins.PluginBase.Configuration):
        # DEPRECATE: 2.2.0
        host = vodka.config.Attribute(
            str,
            default="localhost",
            help_text="host address",
            deprecated="2.2.0, it's being replaced by the 'bind' config attribute"
        )

        # DEPRECATE: 2.2.0
        port = vodka.config.Attribute(
            int,
            default=80,
            help_text="host port",
            deprecated="2.2.0, it's being replaced by the 'bind' config attribute"
        )

        bind = vodka.config.Attribute(
            vodka.config.validators.host,
            default="localhost:80",
            help_text="bind server to this address. e.g localhost:80"
        )

        debug = vodka.config.Attribute(
            bool,
            help_text="run wsgi server in debug mode (if applicable)",
            default=False
        )

        server = vodka.config.Attribute(
            str,
            help_text="specify which wsgi server should be used",
            default="self",
            choices=["uwsgi", "gunicorn", "self", "gevent"]
        )

        static_url_path = vodka.config.Attribute(
            str,
            default="/static",
            help_text="url path where static files can be requested from"
        )

        routes = vodka.config.Attribute(
            dict,
            help_text="routing of request endpoints to vodka application end points",
            default={}
        )

        ssl = vodka.config.Attribute(
            dict,
            help_text="ssl encryption",
            default={},
            handler=SSLConfiguration
        )

    @classmethod
    def set_wsgi_app(cls, app):
        WSGIPlugin.wsgi_application = app

    def init(self):
        if "bind" in self.config:
            (host, port) = self.get_config("bind").split(":")
            self.host = host
            self.port = int(port)

        # DEPRECATE: 2.2.0
        else:
            self.host = self.get_config("host")
            self.port = self.get_config("port")
 

    def setup(self):
       
        self.static_url_prefixes = {}
        for name in list(vodka.instances.keys()):
            self.static_url_prefixes[name] = self.static_url_prefix(name)
        self.set_routes()

    def set_server(self, wsgi_app, fnc_serve=None):
        """
        figures out how the wsgi application is to be served
        according to config
        """

        self.set_wsgi_app(wsgi_app)

        ssl_config = self.get_config("ssl")
        ssl_context = {}

        if self.get_config("server") == "gevent":

            if ssl_config.get("enabled"):
                ssl_context["certfile"] = ssl_config.get("cert")
                ssl_context["keyfile"] = ssl_config.get("key")

            from gevent.pywsgi import WSGIServer

            http_server = WSGIServer(
                (self.host, self.port),
                wsgi_app,
                **ssl_context
            )

            self.log.debug("Serving WSGI via gevent.pywsgi.WSGIServer")

            fnc_serve = http_server.serve_forever

        elif self.get_config("server") == "uwsgi":
            self.config["start_manual"] = True

        elif self.get_config("server") == "gunicorn":
            self.config["start_manual"] = True

        elif self.get_config("server") == "self":
            fnc_serve = self.run

        # figure out async handler

        if self.get_config("async") == "gevent":

            # handle async via gevent
            import gevent

            self.log.debug("Handling wsgi on gevent")

            self.worker = gevent.spawn(fnc_serve)

        elif self.get_config("async") == "thread":

            self.worker = fnc_serve

        else:

            self.worker = fnc_serve

    def run(self):
        pass

    def set_route(self, path, target, methods=None):
        pass

    def static_url_prefix(self, app_name):
        return os.path.join(self.get_config("static_url_path"), app_name, "")

    def request_env(self, req=None, **kwargs):
        renv = {
            "request": req
        }
        for name in list(vodka.instances.keys()):
            appenv = {"static_url" : self.static_url_prefixes.get(name, "")}
            renv[name] = appenv
        renv.update(**kwargs)
        if "url" in kwargs:
            renv["host"] = "%s://%s" % (kwargs["url"].scheme, kwargs["url"].netloc)
        return renv
    
    def set_static_routes(self):
        pass

    def set_routes(self):
        
        self.set_static_routes()

        for path, target in list(self.get_config("routes").items()):

            if type(target) == str:
                target = {"target": target, "methods": ["GET"]}
            elif type(target) == dict:
                if not target.get("methods"):
                    target["methods"] = "GET"

            if target["target"].find("->") > -1:
                # target is an application method
                app_name, fnc_name = tuple(target["target"].split("->"))
                inst = get_instance(app_name)

                # FIXME: if for some reason we want to support different wsgi
                # plugins pointing to methods on the same app in the same
                # instance, this needs to change
                inst.wsgi_plugin = self

                meth = getattr(inst, fnc_name)
                
                # apply route decorators (specified by config keys other than
                # "target" and "methods"
                for k,v in list(target.items()):
                    decorator = getattr(self, "decorate_route_%s" % k, None)
                    if decorator:
                        meth = decorator(**v).__call__(meth)
                
                self.set_route(path, meth,
                               methods=target.get("methods", []))
            else:
                # target is a static path
                # FIXME: handled via static directory routing, probably
                # redundant and not implemented at this point
                continue
