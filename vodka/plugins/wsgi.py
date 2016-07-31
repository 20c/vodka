from vodka import get_instance
import vodka.plugins
import vodka.config


def application():
    return WSGIPlugin.wsgi_application


class WSGIPlugin(vodka.plugins.PluginBase):

    wsgi_application = None

    class Configuration(vodka.plugins.PluginBase.Configuration):

        host = vodka.config.Attribute(
            str,
            help_text="host address"
        )

        port = vodka.config.Attribute(
            int,
            help_text="host port"
        )

        debug = vodka.config.Attribute(
            bool,
            help_text="run wsgi server in debug mode (if applicable)",
            default=False
        )

        static_url_path = vodka.config.Attribute(
            str,
            default="/static",
            help_text="url path where static files can be requested from"
        )

        static_folder = vodka.config.Attribute(
            vodka.config.validators.path,
            help_text="location of static files",
            default=lambda x, i: i.resource("static")
        )

        server = vodka.config.Attribute(
            str,
            help_text="specify which wsgi server should be used",
            default="self",
            choices=["uwsgi", "self", "gevent"]
        )

        routes = vodka.config.Attribute(
            dict,
            help_text="routing of request endpoints to vodka application end points",
            default={}
        )

    @classmethod
    def set_wsgi_app(cls, app):
        WSGIPlugin.wsgi_application = app

    def set_server(self, wsgi_app, fnc_serve=None):
        """
        figures out how the wsgi application is to be served
        according to config
        """

        self.set_wsgi_app(wsgi_app)

        host = self.get_config("host")
        port = self.get_config("port")

        if self.get_config("server") == "gevent":

            # serve via gevent.WSGIServer
            from gevent.wsgi import WSGIServer

            http_server = WSGIServer(
                (host, port),
                wsgi_app
            )

            self.log.debug("Serving WSGI via gevent.WSGIServer")

            fnc_serve = http_server.serve_forever

        elif self.get_config("server") == "uwsgi":
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

        self.set_routes()

    def run(self):
        pass

    def set_route(self, path, target):
        pass

    def request_env(self, req=None, **kwargs):
        renv = {
            "static_url": "%s/" % self.get_config("static_url_path"),
            "request": req
        }
        renv.update(**kwargs)
        return renv

    def set_routes(self):
        for path, target in self.get_config("routes").items():

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

                self.set_route(path, getattr(inst, fnc_name),
                               methods=target.get("methods", []))
            else:
                # target is a static path
                # FIXME: handled via static directory routing, probably
                # redundant and not implemented at this point
                continue
